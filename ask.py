import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA

os.environ["GOOGLE_API_KEY"] = "AIzaSy..."

def main():
    """
    Tuned CLI with better retrieval parameters and session loop.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # Setting temperature to 0 for factual consistency
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    
    # Retrieve top 3 chunks for context
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=vector_db.as_retriever(search_kwargs={"k": 3})
    )
    
    while True:
        q = input("\nmySearch > ")
        if q.lower() == 'exit': break
        res = qa_chain.invoke(q)
        print(f"Result: {res['result']}")

if __name__ == "__main__":
    main()
