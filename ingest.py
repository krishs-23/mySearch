import sys
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def ingest_single_file(filename):
    """
    Initialize the embedding model using Google Gemini.
    """
    file_path = os.path.join("docs", filename)
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    print(f"Embedding initialization successful.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
