# mySearch: Personal Document Intelligence System

mySearch is a high-performance, real-time document indexing and retrieval-augmented generation (RAG) system. It combines a low-latency Java backend for filesystem monitoring with a sophisticated Python frontend leveraging the latest Google Gemini AI models to provide a private, searchable knowledge base.

## Key Features

* **Automated Real-Time Monitoring**: Unlike systems that require manual indexing, mySearch uses a native Java WatchService. This service monitors your docs/ directory at the operating system level, ensuring that the moment a file is saved, it is queued for indexing without any user intervention.
* **Intelligent Multi-Format Ingestion**: The system doesn't just read text; it understands the structure of various file types. Whether it's a multi-page PDF, a complex Excel spreadsheet, or a formatted Word document, the ingestion engine extracts content while maintaining context.
* **State-of-the-Art Semantic Search**: By using Google's text-embedding-004 model, the system moves beyond keyword matching. It creates high-dimensional vector representations of your data, allowing it to find information based on conceptual similarity—even if your query uses different terminology than the source text.
* **Context-Aware RAG Architecture**: The Retrieval-Augmented Generation (RAG) pipeline ensures that the LLM (Gemini 3.0 Flash) only answers based on your private data. This minimizes hallucinations and provides a secure way to interact with your personal documents.
* **Local-First Performance and Privacy**: Your vector index is stored locally using FAISS. This ensures lightning-fast retrieval speeds and keeps the "map" of your data on your machine, using the cloud only for the heavy lifting of embedding and generative reasoning.
* **Resilient Concurrency and Error Handling**: Designed for real-world use, the system handles race conditions via file-level locking and manages API rate limits through an intelligent exponential backoff strategy, making it robust enough for mass document imports.

## How it Works: Under the Hood

The system operates as a cohesive pipeline across three distinct layers:

### 1. The Listener Layer (Java)
The FolderWatcher serves as the vigilant entry point. Built in Java for its superior native filesystem hooks, it registers a WatchService on the docs/ folder. When a CREATE event is triggered, it identifies the new file and spawns a Python subprocess.

### 2. The Ingestion & Vectorization Layer (Python)
Once a file is detected:
* Parsing: The script selects the appropriate loader (e.g., PyPDFLoader, Docx2txtLoader, or a custom Pandas-based loader for Excel/CSV).
* Chunking: Large documents are broken down using a RecursiveCharacterTextSplitter.
* Vectorization: Each chunk is sent to the Google Gemini Embedding API.
* Synchronization: Using portalocker, the system safely opens the local FAISS index, merges the new vectors, and saves it back to disk.

### 3. The Retrieval & Generation Layer (Python CLI)
When you ask a question in ask.py:
* Similarity Search: Your question is vectorized, and FAISS performs a similarity search to find the top 3 most relevant chunks.
* Contextual Injection: These chunks are formatted into a specialized prompt for Gemini 3.0 Flash.
* Generative Response: The LLM synthesizes the final answer.

## Technologies Used

* **Java (NIO WatchService)**: High-efficiency native file system listener.
* **Python (LangChain)**: Orchestration layer for the RAG pipeline.
* **Google Gemini 3.0 Flash**: Primary LLM for rapid, context-aware generation.
* **text-embedding-004**: Advanced embedding model for precise semantic search.
* **FAISS (Facebook AI Similarity Search)**: High-performance local vector database.
* **Portalocker**: Cross-process synchronization for index integrity.

## Supported Document Formats

The ingestion engine is configured to process the following formats in order of priority:

1. Portable Document Format (.pdf)
2. Microsoft Word Documents (.docx, .doc)
3. Standard Text and Markdown (.txt, .md)
4. Comma-Separated Values (.csv)
5. Microsoft Excel Spreadsheets (.xlsx, .xls)

## Detailed Usage Guide

### 1. Initial Setup
Initialize your environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install langchain-google-genai langchain-community faiss-cpu pypdf langchain-classic pandas openpyxl python-docx portalocker python-dotenv
```

Configure your API key in a `.env` file in the project root:
```text
GOOGLE_API_KEY=your_actual_key_here
```

### 2. Launching the Automated Indexer
Compile and start the Java service. This must remain running to detect new files:
```bash
javac FolderWatcher.java
java FolderWatcher
```

### 3. Adding Documents
To index information, simply drop any supported file into the `docs/` folder. The `FolderWatcher` will immediately detect the file and trigger the Python ingestion pipeline. You will see progress logs in the terminal where the Java service is running.

### 4. Searching Your Library
Open a new terminal session and launch the interactive search console:
```bash
python ask.py
```
Once the console is active, you can ask natural language questions such as:
- "Summarize the key points of the quarterly report."
- "What are the specific requirements mentioned in the technical manual?"
- "Compare the findings between the two medical studies."

The system will semantically retrieve relevant sections and provide a concise answer based on your specific documents. Type `exit` to close the session.