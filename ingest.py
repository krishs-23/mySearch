import sys
import os
import time
import portalocker
from dotenv import load_dotenv
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

# Load environment configuration
load_dotenv()

def load_excel(file_path):
    """Parses Excel tabular data for embedding."""
    try:
        df = pd.read_excel(file_path)
        content = df.to_string(index=False)
        return [Document(page_content=content, metadata={"source": file_path})] if content.strip() else []
    except Exception as e:
        print(f"Excel Error: {e}")
        return []

def load_csv(file_path):
    """Parses CSV data reliably using pandas."""
    try:
        df = pd.read_csv(file_path)
        content = df.to_string(index=False)
        return [Document(page_content=content, metadata={"source": file_path})] if content.strip() else []
    except Exception as e:
        print(f"CSV Error: {e}")
        return []

LOADER_MAPPING = {
    ".pdf": lambda p: PyPDFLoader(p),
    ".txt": lambda p: TextLoader(p),
    ".md": lambda p: TextLoader(p),
    ".csv": lambda p: load_csv(p),
    ".docx": lambda p: Docx2txtLoader(p),
    ".xlsx": lambda p: load_excel(p),
}

def ingest_single_file(filename):
    """Primary ingestion pipeline: parse -> chunk -> embed -> save."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in LOADER_MAPPING: return
    file_path = os.path.join("docs", filename)
    if not os.path.exists(file_path): return

    print(f"Processing: {filename}")
    try:
        loader_result = LOADER_MAPPING[ext](file_path)
        raw_docs = loader_result if isinstance(loader_result, list) else loader_result.load()
        if not raw_docs: return

        # Recursive text splitting for semantic context preservation
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        documents = text_splitter.split_documents(raw_docs)
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        db_path = "./faiss_index"
        lock_path = "./faiss_index.lock"
        
        # Concurrent write protection
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
                    print(f"Success: {filename}")
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 10)
                    else: raise e
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1: ingest_single_file(sys.argv[1])
