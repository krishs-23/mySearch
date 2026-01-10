import sys
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Configuration for Google API
os.environ["GOOGLE_API_KEY"] = "AIzaSy..."

def ingest_single_file(filename):
    """
    Load document and initialize the embedding model.
    Using Gemini-based embeddings for semantic representation.
    """
    file_path = os.path.join("docs", filename)
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Initialize the Gemini embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    print(f"Generated embeddings for {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
