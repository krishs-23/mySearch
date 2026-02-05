# Development Guide

## Project Structure
* **FolderWatcher.java**: High-efficiency Java listener that watches the filesystem for changes. It executes the Python backend via subprocess calls.
* **ingest.py**: The primary ingestion engine. Handles document loading, text splitting, embedding generation, and FAISS index management.
* **ask.py**: The user interface. Implements the RAG chain using the vector store and the Gemini LLM.
* **docs/**: The designated folder for document monitoring.
* **faiss_index/**: Local persistence directory for the vectorized document mappings.

## Technical Architecture

### 1. File Monitoring (Java)
We use Java's `WatchService` (part of the `java.nio` package) because it provides native OS notifications. This is far more performant than polling a directory from Python, especially on large filesystems.

### 2. Semantic Search (FAISS)
FAISS (Facebook AI Similarity Search) was selected for its speed and simplicity. It allows for local vector storage without requiring a dedicated database server like Chroma or Pinecone, making the system entirely portable and private.

### 3. AI Pipeline (Gemini)
- **Embedding Model**: `text-embedding-004` generates dense 768-dimensional vectors.
- **LLM**: `gemini-3-flash-preview` is used for the generation stage. Its high-speed inference and large context window make it ideal for RAG applications.

## Key Implementation Challenges

### Concurrency
During mass document imports, multiple instances of the ingestion script may attempt to write to the FAISS index simultaneously. We implemented file-level locking using the `portalocker` library to prevent index corruption.

### Rate Limiting
The Google AI free tier has specific requests-per-minute limits. The ingestion script includes a retry mechanism with exponential backoff to ensure large batches of documents are eventually indexed successfully.

### Document Fragmentation
To improve search accuracy, we use `RecursiveCharacterTextSplitter`. This breaks documents into overlapping chunks (2000 chars with 200 char overlap), ensuring that semantic context isn't lost at the boundaries of a split.

## Future Roadmap
- Integration of OCR for scanned PDF support.
- Web-based dashboard for visual document management.
- Support for remote cloud storage listeners (S3/GCS).
