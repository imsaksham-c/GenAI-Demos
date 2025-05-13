import os
import torch
import lancedb
from dotenv import load_dotenv
from constants import input_pdf
from prompt import rag_prompt
from langchain_community.vectorstores import LanceDB
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from lancedb.embeddings import get_registry
from lancedb.pydantic import Vector, LanceModel
from lancedb.rerankers import ColbertReranker


load_dotenv()


class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}

    def __repr__(self):
        return f"Document(page_content='{self.page_content}', metadata={self.metadata})"


def get_rag_output(question):
    input_pdf_file = input_pdf

    # Create your PDF loader
    loader = PyPDFLoader(input_pdf_file)

    # Load the PDF document
    documents = loader.load()

    # Chunk the financial report
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    openai_model = get_registry().get("openai").create(name="text-embedding-ada-002")

    class Schema(LanceModel):
        text: str = openai_model.SourceField()
        vector: Vector(1536) = openai_model.VectorField()

    embedding_function = OpenAIEmbeddings()

    db = lancedb.connect("/tmp/langchain")
    
    table = db.create_table("airbnb", schema=Schema, mode="overwrite")

    # Load the document into LanceDB
    langchain_rerank = LanceDB.from_documents(docs, embedding_function, connection=table)
    table.create_fts_index("text", replace=True)

    #reranker = ColbertReranker()
    docs_n = (
        table.search(question, query_type="hybrid")
        .limit(5)
        .to_pandas()["text"]
        .to_list()
    )

    metadata = {"source": input_pdf_file}
    docs_with_metadata = [
        Document(page_content=text, metadata=metadata) for text in docs_n
    ]

    table_re = db.create_table("retreiver", schema=Schema, mode="overwrite")

    # Load the document into LanceDB
    vectorstore = LanceDB.from_documents(docs_with_metadata, embedding_function, connection=table_re)

    retriever = vectorstore.as_retriever()

    rag_prompt_template = rag_prompt

    prompt = PromptTemplate(
        template=rag_prompt_template,
        input_variables=[
            "context",
            "question",
        ],
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    output = rag_chain.invoke(question)
    return output
