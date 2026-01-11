import sys
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

os.environ["GOOGLE_API_KEY"] = "AIzaSy..."

def ingest_single_file(filename):
    """
    Processes document and saves the vector representation to a local FAISS index.
    """
    file_path = os.path.join("docs", filename)
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create and save the FAISS vector store locally
    db = FAISS.from_documents(documents, embeddings)
    db.save_local("./faiss_index")
    print(f"Saved local FAISS index.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
