import sys
import os
from langchain_community.document_loaders import PyPDFLoader

def ingest_single_file(filename):
    """
    Initial implementation: Load a PDF and report page count.
    """
    file_path = os.path.join("docs", filename)
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_single_file(sys.argv[1])
