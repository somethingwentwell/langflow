from langflow import CustomComponent

from langchain.llms.base import BaseLLM
from langchain.schema import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever
import os

class InSourcePostgresVectorEmbedding(CustomComponent):
    display_name: str = "Postgres Vector Embedding (InSource)"
    description: str = "Embed document data into a Postgres vector database"
    documentation: str = "https://insource.asia"
    field_config = {
        "code": {"show": False}
    }

    def build(self, collection_name: str, llm: BaseLLM, embeddings: OpenAIEmbeddings ,docs: Document) -> BaseRetriever:
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            database=os.environ.get("POSTGRES_DATABASE", "postgres"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        )
        COLLECTION_NAME = collection_name
        
        # db = PGVector.from_documents(
        #     embedding=embeddings,
        #     documents=docs,
        #     collection_name=COLLECTION_NAME,
        #     connection_string=CONNECTION_STRING
        # )
        
        
        db = PGVector.from_documents(
            embedding=embeddings,
            documents=docs,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
            pre_delete_collection=True
        )
        
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="map_reduce", retriever=db.as_retriever(), return_source_documents=True, verbose=True)
        
        return qa
