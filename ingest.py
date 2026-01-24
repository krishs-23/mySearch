import sys, os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def ingest_single_file(filename):
    if not filename.lower().endswith(".pdf"): return
    file_path = os.path.join("docs", filename)
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        if os.path.exists("./faiss_index"):
            db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
            db.add_documents(documents)
        else:
            db = FAISS.from_documents(documents, embeddings)
        db.save_local("./faiss_index")
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1: ingest_single_file(sys.argv[1])
