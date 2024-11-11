from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

os.getenv("OPENAI_API_KEY")


def load_document_and_split_text(document):
    doc = PyPDFLoader(document)
    docs = doc.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500)
    doc_split = splitter.split_documents(docs)
    return doc_split


# chroma db
def chroma_db_embeddings(embedding, doc_split):
    chroma = Chroma()
    vector_db = chroma.from_documents(embedding=embedding, documents=doc_split)
    return vector_db


def response_to_query(query, doc_split):
    embedding = OpenAIEmbeddings()
    vector_db = chroma_db_embeddings(embedding, doc_split)
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    qa_prompt = ChatPromptTemplate.from_template(
        """
        Answer the questions based on the provided context only.
        Please provide the most accurate response based on the question.
        <context>
        {context}
        <context>
        Question: {input}
        """
    )
    llm_model = ChatOpenAI()
    output_parser = StrOutputParser()

    qa_chain = (
        {"context": retriever, "input": RunnablePassthrough()}
        | qa_prompt
        | llm_model
        | output_parser
    )

    response = qa_chain.invoke(query)
    return response
