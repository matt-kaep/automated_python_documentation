import os

from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import (
    AzureOpenAIEmbeddings,
    HuggingFaceEmbeddings,
    OpenAIEmbeddings,
)
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

# EMBEDDINGS
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


class ChatPDF:
    vector_store = None
    retriever = None
    chain = None

    os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "your_openai_endpoint"
    os.environ["AZURE_OPENAI_API_KEY"] = "your_openai_api_key"
    os.environ["openai_api_key"] = "your_openai_api_key"

    def __init__(self):
        """
        Summary: Initializes an instance of the class.

        Parameters:
        - azure_deployment (str): The deployment version of Azure Chat OpenAI.
        - api_version (str): The version of the API to be used.
        - temperature (int): The temperature parameter for generating responses.
        - max_tokens (int): The maximum number of tokens in the generated response.
        - timeout (int): The timeout duration for API requests.
        - max_retries (int): The maximum number of retries for API requests.

        Returns: None
        """

        self.model = AzureChatOpenAI(
            azure_deployment="gpt4_32k",
            api_version="2024-05-01-preview",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # organization="...",
            # # other params...
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        self.prompt_template = ChatPromptTemplate.from_template(
            template="""Answer the question based only on the following context:{context}
                                                                Question: {question}"""
        )

    def ingest(self, file_path: str):
        """
        Summary:
        This function ingests a PDF file and performs several operations on the text data extracted from the file. It splits the text into chunks, filters out complex metadata, converts the chunks into vector representations using a specified embedding model, and sets up a retriever for similarity-based search. Finally, it sets up a processing chain for further text processing and output parsing.

        Parameters:
        - file_path (str): The path to the PDF file to be ingested.

        Returns:
        None
        """

        docs = PyPDFLoader(file_path=file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        # vector_store = Chroma.from_documents(chunks, embeddings = AzureOpenAIEmbeddings(azure_deployment="eleven_embedding_ada_002",
        #                                                                                 openai_api_version="2023-05-15",
        #                                                                                 openai_api_key="4a8f724e3ef84157bc5378553d3dec14",
        #                                                                                 openai_api_base="https://elevengpt.openai.azure.com/"
        #                                                                                 ))

        vector_store = Chroma.from_documents(
            chunks, embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        )
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 10,
                "score_threshold": 0.1,
            },
        )
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt_template
            | self.model
            | StrOutputParser()
        )

    def ask(self, query: str):
        """
        Summary:
        This function takes a query as input and performs a series of operations based on the query. If the 'chain' attribute is empty, it returns a message asking to add a PDF document. Otherwise, it prints the string 'retriever fuck' and the result of invoking the 'retriever' attribute with the query. Finally, it returns the result of invoking the 'chain' attribute with the query.

        Parameters:
        - query (str): The query to be processed by the function.

        Returns:
        - str: If the 'chain' attribute is empty, it returns a message asking to add a PDF document. Otherwise, it returns the result of invoking the 'chain' attribute with the query.
        """

        if not self.chain:
            return "Please, add a PDF document first."
        print("retriever fuck")
        print("retriever", self.retriever.invoke(query))
        return self.chain.invoke(query)

    def clear(self):
        """
        Summary:
        Clears the vector_store, retriever, and chain attributes of the object.

        Parameters:
        None

        Returns:
        None
        """

        self.vector_store = None
        self.retriever = None
        self.chain = None
