import sys
import os
import portalocker
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def ingest_single_file(filename):
    # Implementation...
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Preventing concurrent file corruption during rapid indexing
    with portalocker.Lock("./faiss_index.lock", timeout=60):
        if os.path.exists("./faiss_index"):
            db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
            # update logic...
