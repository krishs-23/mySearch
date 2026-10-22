# mySearch: Personal Document Intelligence System

mySearch is a command-line prototype for searching a personal document collection and generating answers from retrieved text. It combines a Java filesystem watcher with Python document ingestion and a LangChain retrieval-augmented generation (RAG) pipeline. FAISS stores the vector index on disk, while Google's Gemini APIs provide embeddings and answer generation.

The project explores how filesystem events, document parsing, chunking, vector retrieval, and an external language-model API fit together. Its current scope is a single local `docs/` directory and a terminal question-and-answer interface. It does not include a web UI, document synchronization, or measured retrieval/performance benchmarks.

## Key Features

* **Automatic ingestion of newly created files:** Java's `WatchService` listens for `ENTRY_CREATE` events in `docs/` and invokes the Python ingestion script. Each subprocess finishes before the watcher processes the next event.
* **Six document formats:** The ingestion mapping accepts PDF, DOCX, TXT, Markdown, CSV, and XLSX files. Document loaders extract text; CSV and Excel inputs are converted into textual tables with pandas.
* **Overlapping text chunks:** A recursive character splitter uses a configured chunk size of 2,000 characters and an overlap of 200 characters. Actual chunk boundaries depend on the extracted text and splitter behavior.
* **Persistent vector retrieval:** Document embeddings are stored in a local FAISS index. Subsequent ingestion loads the existing index and appends new document chunks.
* **Retrieval-augmented answers:** Natural-language queries retrieve up to three relevant chunks for a Gemini model to use as context when producing an answer.
* **Write coordination and bounded retries:** Ingestion uses a shared file lock around index loading, updates, and saves. Errors containing `429` trigger up to two delayed retries, after 10 and 20 seconds.
* **Local index storage with cloud processing:** Index files remain on your machine. Extracted document chunks are sent to Google for embeddings, queries are embedded through Google, and retrieved context is sent to the generation model. This is not an offline-only system.

## How it Works: Under the Hood

### 1. The Listener Layer (Java)

[`FolderWatcher.java`](FolderWatcher.java) registers the top-level `./docs` directory with Java NIO's `WatchService`.

For each creation event, it passes the new entry's filename to:

```text
./venv/bin/python ingest.py <filename>
```

The subprocess inherits terminal input/output, and the watcher calls `waitFor()` before handling the next event. This makes the current watcher sequential; it is not a parallel worker pool.

The directory must exist when the watcher starts. Only creation events are registered: modifications and deletions are not synchronized, subdirectories are not watched recursively, and files already present at startup are not automatically scanned. The hardcoded Python path assumes a macOS/Linux-style virtual environment.

### 2. The Ingestion & Vectorization Layer (Python)

[`ingest.py`](ingest.py) handles one filename at a time:

1. **Resolve the input:** determine the lowercase file extension and join the supplied filename to `docs/`. Unsupported extensions and nonexistent paths return without ingestion.
2. **Extract content:** PDF, text, Markdown, and DOCX use document loaders. CSV and XLSX use pandas, converting the resulting table to text with `to_string(index=False)`.
3. **Split text:** use `RecursiveCharacterTextSplitter` with `chunk_size=2000` and `chunk_overlap=200`.
4. **Configure embeddings:** instantiate `GoogleGenerativeAIEmbeddings` with the model identifier currently in the source: `models/text-embedding-004`.
5. **Acquire the write lock:** use `portalocker.Lock` on `./faiss_index.lock`, with a 60-second lock-acquisition timeout.
6. **Update the index:** load `./faiss_index` if present and call `add_documents`; otherwise create an index from the chunks. Save the result to disk.
7. **Handle failures:** print a failure message for exceptions. Inside the locked index-update block, errors whose string contains `429` are retried up to three total attempts.

The retry waits are **linear delays of 10 and 20 seconds**, not exponential backoff. The lock is held during embedding/index operations and those waits. It coordinates ingestion processes using the same lock file; it does not make all reader/writer activity atomic or guarantee recovery from interrupted saves.

Source metadata from the loaders is retained with the documents, but the current query UI prints only the generated answer.

### 3. The Retrieval & Generation Layer (Python CLI)

[`ask.py`](ask.py) loads environment variables, checks for the index directory, and loads the FAISS index once when the process starts.

It then creates:

- A query embedding client using `models/text-embedding-004`.
- A chat client using the configured identifier `gemini-3-flash-preview`, with temperature `0`.
- A LangChain `RetrievalQA` chain with a retriever configured as `search_kwargs={"k": 3}`.

Each question is embedded for similarity search. The chain supplies the retrieved text to the language model and prints the returned `result`. Enter `exit` or `quit` to leave the console.

Because the index is loaded once, restart `ask.py` after new ingestion completes to search the updated index. The console does not currently display source citations, a relevance threshold, or a custom answer-verification step. RAG supplies document context but does not guarantee that every answer is correct or exclusively supported by the files.

## Technologies Used

| Technology | Current role |
| --- | --- |
| Java NIO `WatchService` | Detect top-level file-creation events and launch ingestion subprocesses. |
| Python | Implement extraction, chunking, indexing, and the interactive query loop. |
| LangChain | Provide document loaders, splitting, vector-store integration, and the retrieval/generation chain. |
| Google Gemini APIs | Generate embeddings and answers using the model identifiers configured in the source. |
| FAISS | Store and search the local vector index through LangChain's integration. |
| pandas / openpyxl | Read CSV and XLSX tables and render them as text for ingestion. |
| pypdf / docx2txt | Extract content from PDF and DOCX files through the document loaders. |
| portalocker | Coordinate ingestion writes through a shared lock file. |
| python-dotenv | Load `GOOGLE_API_KEY` from a local `.env` file. |

The model names above describe the checked-in configuration, not a guarantee of current API availability or access for every account. The repository does not pin dependency versions or include an automated compatibility test. Model availability, quotas, and package compatibility must be checked in the environment where you run it.

## Supported Document Formats

| Format | Extension | Current extraction behavior |
| --- | --- | --- |
| Portable Document Format | `.pdf` | `PyPDFLoader` extracts text. There is no separate OCR stage for scanned, image-only pages. |
| Microsoft Word | `.docx` | `Docx2txtLoader` extracts document text. |
| Plain text | `.txt` | `TextLoader` reads the file. |
| Markdown | `.md` | `TextLoader` treats Markdown as text; there is no dedicated structural Markdown parser. |
| Comma-separated values | `.csv` | `pandas.read_csv` reads a table and converts it into a text document. |
| Microsoft Excel | `.xlsx` | `pandas.read_excel` uses its defaults, including the first worksheet, and converts it into a text document. |

Legacy `.doc` and `.xls` files are **not** included in the extension mapping. Convert them to a supported format first.

Extraction produces text suitable for chunking; it does not preserve full document layout, images, or workbook structure. Spreadsheet/CSV display formatting may truncate large tables under pandas' display settings, so inspect extracted content before relying on complete coverage.

## Detailed Usage Guide

### 1. Initial Setup

The automatic watcher instructions below target macOS/Linux because its subprocess path is `./venv/bin/python`. Install Python with virtual-environment support and a JDK with both `java` and `javac` on PATH.

Clone the repository and run commands from its root:

```bash
git clone https://github.com/krishs-23/mySearch.git
cd mySearch
mkdir -p docs
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install langchain-google-genai langchain-community langchain-core langchain-text-splitters langchain-classic faiss-cpu pypdf docx2txt pandas openpyxl portalocker python-dotenv
```

This dependency list includes `docx2txt`, which is used by the configured DOCX loader. Installing `python-docx` alone does not provide that loader's extraction dependency.

Create a file named `.env` in the project root:

```text
GOOGLE_API_KEY=your_actual_key_here
```

Use a Google API key authorized for the configured embedding and generation models. Keep the real key out of commits, screenshots, and logs. A local vector index does not eliminate API usage, quota limits, or any charges associated with your account.

The install command is an unpinned starting point. If a package update changes compatibility, record the working versions for your environment; this repository currently has no requirements file or lockfile.

### 2. Launching the Automated Indexer

From the repository root:

```bash
javac FolderWatcher.java
java FolderWatcher
```

Keep this terminal running. It prints the absolute directory being monitored, and ingestion subprocesses print progress in the same terminal. Use Ctrl+C to stop the watcher.

Run the watcher from the root so it can find `docs/`, `ingest.py`, and `venv/bin/python`. The Python virtual environment does not need to be activated in this terminal if it exists at the exact hardcoded path.

On Windows, the automatic watcher requires a source change to use the Windows virtual-environment Python path. The manual ingestion and query scripts can instead be invoked with the Python executable from an appropriately configured environment.

### 3. Adding Documents

For a first run, create a small UTF-8 text file in `docs/` **after** starting the watcher. For example, save a file named `sample.txt` containing a few factual sentences, then wait for `Success: sample.txt` in the watcher terminal.

New supported files trigger ingestion, but the watcher does not wait for a file copy or save to finish. If extraction fails while a file is still being written, wait until it is complete and ingest it manually:

```bash
source venv/bin/activate
python ingest.py sample.txt
```

Pass the filename relative to `docs/`, not `docs/sample.txt`: the script adds the `docs` prefix itself. Quote filenames that contain spaces:

```bash
python ingest.py "lecture notes.pdf"
```

Manual ingestion also handles files that were already present before the watcher started. Avoid manually re-ingesting files that were successfully indexed unless you intend to append another copy of their chunks; the implementation has no duplicate detection.

### 4. Searching Your Library

After ingestion finishes, open a second terminal:

```bash
cd mySearch
source venv/bin/activate
python ask.py
```

Use `cd mySearch` from the repository's parent directory, or enter the repository's absolute path if your new terminal starts elsewhere.

The console displays `Query >`. Ask questions whose answers are present in the indexed files, such as:

- "What deadline is listed for the final project?"
- "Which steps does the installation guide require?"
- "How does this document define a binary search tree?"

If you indexed the sample file, first ask a question with an obvious answer from that file to check the end-to-end flow. Retrieval is limited to up to three chunks per question, so a broad request to compare or summarize many documents may not retrieve all relevant evidence.

If the index directory is missing, the script prints `Knowledge base empty.` and exits. Ingest a supported document before starting it again. Restart the console whenever you want it to load a newly updated index.

### 5. Index Lifecycle and Data Handling

- **Updates and deletions:** editing, renaming, or deleting source files does not reliably synchronize their indexed content. Deleting a document from `docs/` does not remove its existing vectors.
- **Re-indexing:** the current pipeline appends chunks. To build a fresh index, stop the watcher and query process, move the existing `faiss_index/` directory aside, manually ingest each desired file once, and restart the processes.
- **Model changes:** if you change the embedding model, update both `ingest.py` and `ask.py` and rebuild the index with the same embedding model used for queries.
- **Index trust:** both scripts load indexes with `allow_dangerous_deserialization=True`. Only load indexes you created and control; do not use untrusted downloaded index files.
- **Cloud processing:** extracted chunks, query text, and retrieved context leave the local machine for their respective Google API operations. Choose documents appropriate for that processing.
- **Concurrent access:** the ingestion lock does not cover query-side loading. Start or restart the query process after an index write completes.

### 6. Troubleshooting and Current Limitations

| Symptom | What to check |
| --- | --- |
| Watcher cannot start | Confirm `docs/` exists and that the working directory is the repository root. |
| Python subprocess cannot launch | Confirm `venv/bin/python` exists; the checked-in watcher does not select an arbitrary active environment. |
| Existing file is not indexed | Files present before startup do not emit a new creation event; use manual ingestion. |
| New file fails to parse | Wait for the copy/save to finish, check the file format, and retry manually. |
| DOCX loader reports a missing dependency | Install `docx2txt` inside the environment used by the watcher. |
| Authentication, model, or quota errors | Check the API key, account access, configured model identifiers, and quota. Only errors containing `429` receive the explicit delayed retries. |
| Search ignores a newly indexed document | Restart `ask.py` after ingestion finishes. |
| Old or duplicated content appears | The index is append-only; rebuild it from the intended source documents. |
| Answer is incomplete or unsupported | Inspect the source material; three retrieved chunks and a generated answer do not constitute a correctness guarantee. |

The current repository has no automated tests, retrieval-quality evaluation, source-citation UI, startup scan, document replacement/deletion logic, or benchmark results. Terminal messages provide basic visibility, but ingestion catches exceptions and does not consistently communicate failure through a nonzero process exit status.

Useful next steps include dependency pinning, test fixtures, mocked API tests, content-hash tracking, safe index replacement, source display, and a small evaluation set with known relevant passages. These are future improvements rather than current capabilities.
