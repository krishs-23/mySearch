import sys
import os
from langchain_community.document_loaders import PyPDFLoader

def ingest_single_file(filename):
    """
    Load a PDF file and print page count.
    Basic implementation for initial testing.
    """
    file_path = os.path.join("docs", filename)
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"Ingested {len(documents)} pages.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
