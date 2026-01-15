import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

os.environ["GOOGLE_API_KEY"] = "AIzaSy..."

def main():
    """
    Main CLI for querying the indexed documents.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Load the persisted FAISS index
    vector_db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vector_db.as_retriever())
    
    query = input("Search: ")
    print(qa_chain.invoke(query))

if __name__ == "__main__":
    main()
