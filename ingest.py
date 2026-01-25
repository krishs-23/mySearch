import sys, os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
LOADER_MAPPING = {".pdf": PyPDFLoader, ".txt": TextLoader, ".md": TextLoader}

def ingest_single_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in LOADER_MAPPING: return
    file_path = os.path.join("docs", filename)
    loader = LOADER_MAPPING[ext](file_path)
    documents = loader.load()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = FAISS.from_documents(documents, embeddings)
    db.save_local("./faiss_index")

if __name__ == "__main__":
    if len(sys.argv) > 1: ingest_single_file(sys.argv[1])
