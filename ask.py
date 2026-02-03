import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA

# Global configuration
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCWBmZeHbC8-NNC9HJJkStkG7t5NQ20_b8"

def main():
    """Main terminal loop for document-based Q&A."""
    # Ensure embedding model matches ingestion (text-embedding-004)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    db_path = "./faiss_index"

    if not os.path.exists(db_path):
        print("Knowledge base is empty. Add documents to 'docs/' first.")
        return

    # Load local vector store
    vector_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    
    # Initialize the latest Gemini Flash model for high-speed generation
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    
    # Configure RAG chain to pull top 3 relevant sections
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=vector_db.as_retriever(search_kwargs={"k": 3})
    )

    print("\n=== mySearch Assistant ===")
    print("Commands: 'exit' or 'quit' to close.\n")

    while True:
        try:
            q = input("Query > ")
            if q.lower() in ['exit', 'quit']: break
            
            # Run inference
            res = qa_chain.invoke(q)
            print(f"\nResponse: {res['result']}\n")
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Search Error: {e}")

if __name__ == "__main__":
    main()
