import sys
import os
import time
import portalocker
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    CSVLoader, 
    Docx2txtLoader
)
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

# Global API Key management
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCWBmZeHbC8-NNC9HJJkStkG7t5NQ20_b8"

# ------------------------------------------------------------------------------
# Custom Loaders
# ------------------------------------------------------------------------------

def load_excel(file_path):
    """Handles Excel files by converting sheets to clean text data."""
    try:
        df = pd.read_excel(file_path)
        content = df.to_string(index=False)
        if not content.strip(): return []
        return [Document(page_content=content, metadata={"source": file_path})]
    except Exception as e:
        print(f"Excel Load Error: {e}")
        return []

def load_csv(file_path):
    """Manual CSV parsing for consistent results across different delimiters."""
    try:
        df = pd.read_csv(file_path)
        content = df.to_string(index=False)
        if not content.strip(): return []
        return [Document(page_content=content, metadata={"source": file_path})]
    except Exception as e:
        print(f"CSV Load Error: {e}")
        return []

# Unified mapping for document types
LOADER_MAPPING = {
    ".pdf": lambda p: PyPDFLoader(p),
    ".txt": lambda p: TextLoader(p),
    ".md": lambda p: TextLoader(p),
    ".csv": lambda p: load_csv(p),
    ".docx": lambda p: Docx2txtLoader(p),
    ".doc": lambda p: Docx2txtLoader(p),
    ".xlsx": lambda p: load_excel(p),
    ".xls": lambda p: load_excel(p),
}

# ------------------------------------------------------------------------------
# Core Ingestion Logic
# ------------------------------------------------------------------------------

def ingest_single_file(filename):
    """Processes a document: loads, splits into chunks, and updates the local index."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in LOADER_MAPPING: return
    file_path = os.path.join("docs", filename)
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return

    print(f"Processing: {filename}")
    try:
        # Load and parse content
        loader_result = LOADER_MAPPING[ext](file_path)
        raw_documents = loader_result if isinstance(loader_result, list) else loader_result.load()
        if not raw_documents: return

        # Recursive splitting to maintain context and satisfy token limits
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        documents = text_splitter.split_documents(raw_documents)
        
        # Initialize modern Gemini embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        db_path = "./faiss_index"
        lock_path = "./faiss_index.lock"
        
        # Guard index file against parallel write corruption
        with portalocker.Lock(lock_path, timeout=60):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if os.path.exists(db_path):
                        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
                        db.add_documents(documents)
                    else:
                        db = FAISS.from_documents(documents, embeddings)
                    db.save_local(db_path)
                    print(f"Indexed: {filename}")
                    break
                except Exception as e:
                    # Implement exponential backoff for API rate limits
                    if "429" in str(e) and attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 10)
                    else: raise e
    except Exception as e:
        print(f"Ingestion Failure for {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
