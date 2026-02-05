# Development Guide

## Project Structure
* **FolderWatcher.java**: Native Java listener for filesystem events.
* **ingest.py**: Backend engine for document vectorization.
* **ask.py**: Interactive RAG CLI for semantic querying.

## Technical Architecture
We utilize Java's WatchService for low-overhead filesystem hooks, which trigger Python subprocesses. The Python layer handles document segmentation and interacts with the Gemini API for embeddings and text generation. FAISS serves as our local, disk-persistent vector storage.

## Implementation Notes
* **Concurrency**: We use file-level locking to prevent index corruption during simultaneous indexing tasks.
* **Rate Limits**: The system implements exponential backoff to respect Google AI free tier quotas.
* **Splitting**: Recursive character splitting ensures that semantic context is preserved across document fragments.
