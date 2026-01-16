import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA

load_dotenv()

def main():
    """
    Interactive search loop with tuned retrieval parameters.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vector_db.as_retriever(search_kwargs={"k": 3}))
    while True:
        q = input("\nmySearch > ")
        if q.lower() == 'exit': break
        print(qa_chain.invoke(q))

if __name__ == "__main__":
    main()
