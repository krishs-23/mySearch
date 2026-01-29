import sys
import os
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

def load_excel(file_path):
    """Custom helper for Excel data extraction."""
    df = pd.read_excel(file_path)
    return [Document(page_content=df.to_string())]

LOADER_MAPPING = {
    ".pdf": PyPDFLoader, ".txt": TextLoader, ".md": TextLoader,
    ".docx": Docx2txtLoader, ".xlsx": load_excel
}

def ingest_single_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in LOADER_MAPPING: return
    
    file_path = os.path.join("docs", filename)
    loader_result = LOADER_MAPPING[ext](file_path)
    documents = loader_result if isinstance(loader_result, list) else loader_result.load()
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = FAISS.from_documents(documents, embeddings)
    db.save_local("./faiss_index")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
