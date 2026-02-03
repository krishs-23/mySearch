import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA

load_dotenv()

def main():
    """Terminal Q&A loop for document interaction."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    db_path = "./faiss_index"

    if not os.path.exists(db_path):
        print("Knowledge base empty.")
        return

    vector_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vector_db.as_retriever(search_kwargs={"k": 3}))

    print("\n=== mySearch Console ===")
    while True:
        try:
            q = input("Query > ")
            if q.lower() in ['exit', 'quit']: break
            print(f"\nResponse: {qa_chain.invoke(q)['result']}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__": main()
