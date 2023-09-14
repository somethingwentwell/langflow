from langflow import CustomComponent

from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.schema import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever
import os

class InSourcePostgresVectorRetriever(CustomComponent):
    display_name: str = "Postgres Vector Retriever (InSource)"
    description: str = "Langchain Retriever for Postgres vector database"
    documentation: str = "https://insource.asia"
    field_config = {
        "code": {"show": False}
    }

    def build(self, collection_name: str, embeddings: OpenAIEmbeddings) -> BaseRetriever:
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            database=os.environ.get("POSTGRES_DATABASE", "postgres"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        )
        COLLECTION_NAME = collection_name
        
        db = PGVector(
            connection_string=CONNECTION_STRING,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
        )
        
        
        return db.as_retriever()
