import sys
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Mapping extensions to appropriate loaders
LOADER_MAPPING = {".pdf": PyPDFLoader, ".txt": TextLoader, ".md": TextLoader}

def ingest_single_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in LOADER_MAPPING: return
    
    file_path = os.path.join("docs", filename)
    loader = LOADER_MAPPING[ext](file_path)
    documents = loader.load()
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    if os.path.exists("./faiss_index"):
        db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
        db.add_documents(documents)
    else:
        db = FAISS.from_documents(documents, embeddings)
    db.save_local("./faiss_index")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
