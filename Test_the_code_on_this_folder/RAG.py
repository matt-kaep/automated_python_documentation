from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import HumanMessage
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from langchain_community.vectorstores.utils import filter_complex_metadata

#EMBEDDINGS
from langchain_community.embeddings import FastEmbedEmbeddings


class ChatPDF:
    vector_store = None
    retriever = None
    chain = None

    os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://elevengpt.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "4a8f724e3ef84157bc5378553d3dec14"
    os.environ["openai_api_key"] = "4a8f724e3ef84157bc5378553d3dec14"

    def __init__(self):
        self.model = AzureChatOpenAI(azure_deployment="gpt4_32k",
                                    api_version="2024-05-01-preview",
                                    temperature=0,
                                    max_tokens=None,
                                    timeout=None,
                                    max_retries=2,
                                    # organization="...",
                                    # # other params...
                                    )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 100)
        self.prompt_template = ChatPromptTemplate.from_template(template = """Answer the question based only on the following context:{context}
                                                                Question: {question}"""
                                                                )
    
    def ingest(self, file_path: str):
        docs = PyPDFLoader(file_path = file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        # vector_store = Chroma.from_documents(chunks, embeddings = AzureOpenAIEmbeddings(azure_deployment="eleven_embedding_ada_002",
        #                                                                                 openai_api_version="2023-05-15",
        #                                                                                 openai_api_key="4a8f724e3ef84157bc5378553d3dec14",
        #                                                                                 openai_api_base="https://elevengpt.openai.azure.com/"
        #                                                                                 ))

        vector_store = Chroma.from_documents(chunks, embedding =  HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 10,
                "score_threshold": 0.1,
            },
        )
        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                      | self.prompt_template
                      | self.model
                      | StrOutputParser())

    def ask(self, query: str):
        if not self.chain:
            return "Please, add a PDF document first."
        print("retriever fuck")
        print("retriever",self.retriever.invoke(query))
        return self.chain.invoke(query)

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
