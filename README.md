# mySearch: Personal Document Intelligence System

mySearch is a high-performance, real-time document indexing and retrieval-augmented generation (RAG) system. It combines a low-latency Java backend for filesystem monitoring with a sophisticated Python frontend leveraging the latest Google Gemini AI models to provide a private, searchable knowledge base.

## Key Features

* Automated Monitoring: Native Java WatchService monitors the filesystem for sub-millisecond detection of new content.
* Broad Format Support: Seamlessly indexes PDF, DOCX, TXT, MD, CSV, and Excel files.
* AI-Driven Retrieval: Built on Gemini 3.0 Flash and text-embedding-004 for high-accuracy semantic search.
* Local Performance: Utilizes FAISS for high-speed vector similarity searches and local metadata persistence.
* Resilient Design: Includes robust concurrency handling and automatic API rate-limit management.

## Technologies Used

* Java (NIO WatchService): Serves as the high-efficiency file system listener.
* Python (LangChain): Acts as the orchestration layer for the RAG pipeline.
* Google Gemini 3.0 Flash: The primary large language model (LLM) used for generating answers.
* text-embedding-004: State-of-the-art embedding model for precise semantic mapping.
* FAISS: High-performance local vector database for similarity searches.
* Portalocker: Provides file-level locking to maintain index stability during parallel indexing.

## Setup and Installation

1. Initialize Environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install langchain-google-genai langchain-community faiss-cpu pypdf langchain-classic pandas openpyxl python-docx portalocker
   ```

2. Configure API Credentials:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

3. Start monitoring and search services according to the usage guide.

## Basic Usage

To index and search your documents:
1. Place your desired documents (PDF, Word, etc.) into the docs/ directory.
2. Verify the FolderWatcher is active to initiate the automated indexing process.
3. Execute ask.py to start the terminal-based query interface and ask questions about your library.
