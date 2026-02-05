# mySearch: Personal Document Intelligence System

mySearch is a high-performance, real-time document indexing and retrieval-augmented generation (RAG) system. It combines a low-latency Java backend for filesystem monitoring with a sophisticated Python frontend leveraging the latest Google Gemini AI models to provide a private, searchable knowledge base.

## Key Features

* **Automated Real-Time Monitoring**: Native Java WatchService monitors your docs/ directory at the operating system level for instant indexing.
* **Intelligent Multi-Format Ingestion**: Supports PDF, Word, Excel, CSV, Text, and Markdown.
* **State-of-the-Art Semantic Search**: Uses Google's text-embedding-004 model for conceptual similarity mapping.
* **Context-Aware RAG Architecture**: Ensures Gemini 3.0 Flash answers only based on your private document context.
* **Local-First Privacy**: Vector indices are stored locally using FAISS.
* **Resilient Concurrency**: Implements file-level locking and intelligent API rate-limit management.

## Technologies Used

* **Java (NIO WatchService)**: High-efficiency native file system listener.
* **Python (LangChain)**: Orchestration layer for the RAG pipeline.
* **Google Gemini 3.0 Flash**: Primary LLM for rapid, context-aware generation.
* **text-embedding-004**: Advanced embedding model for precise semantic search.
* **FAISS**: Local vector database for lightning-fast similarity lookups.
* **Portalocker**: Cross-process synchronization for index integrity.

## Setup and Installation

1. Initialize Environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install langchain-google-genai langchain-community faiss-cpu pypdf langchain-classic pandas openpyxl python-docx portalocker python-dotenv
   ```

2. Configure API Credentials:
   Create a .env file in the root directory:
   ```
   GOOGLE_API_KEY=your_actual_key_here
   ```

3. Start Service:
   ```bash
   javac FolderWatcher.java
   java FolderWatcher
   ```

4. Search:
   ```bash
   python ask.py
   ```
