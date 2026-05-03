import logging
import os
from typing import List, Dict, Any, Optional
from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import DashScopeEmbeddings
from muggle.infra.config import cfg

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        params = cfg.get_vector_store_params()
        self.uri = params["uri"]
        self.token = params["token"]
        self.collection_name = params["collection_name"]
        self.embedding_model = params["embedding_model"]
        self.top_k = params.get("top_k", 3)
        
        # Initialize Milvus Client
        self.client = MilvusClient(uri=self.uri, token=self.token)
        
        # Initialize Embeddings
        self.embeddings = DashScopeEmbeddings(
            model=self.embedding_model,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        
        self._initialize_collection()

    def _initialize_collection(self):
        if self.client.has_collection(self.collection_name):
            logger.info(f"Collection {self.collection_name} already exists.")
            return

        # Define Schema
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=64, is_primary=True)
        schema.add_field(field_name="header_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="content_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2048)
        schema.add_field(field_name="header", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="is_segment", datatype=DataType.BOOL)

        # Define Index Parameters
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="header_vector",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        index_params.add_index(
            field_name="content_vector",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )

        # Create Collection
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        logger.info(f"Created collection {self.collection_name} with dual-vector schema.")

    def insert(self, data: List[Dict[str, Any]]):
        """Insert records into the collection."""
        if not data:
            return
        return self.client.insert(collection_name=self.collection_name, data=data)

    def upsert(self, data: List[Dict[str, Any]]):
        """Upsert records into the collection for idempotency."""
        if not data:
            return
        return self.client.upsert(collection_name=self.collection_name, data=data)

    def search(self, 
               query_text: str, 
               vector_field: str = "content_vector", 
               limit: int | None = None,
               filter: str = "") -> List[Dict[str, Any]]:
        """Perform similarity search using query text."""
        query_vector = self.embeddings.embed_query(query_text)
        
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field=vector_field,
            limit=limit if limit is not None else self.top_k,
            filter=filter,
            output_fields=["text", "header", "is_segment"]
        )
        # Flatten results
        return [res["entity"] for res in results[0]] if results else []

    def embed_text(self, text: str) -> List[float]:
        """Utility to embed a single text string."""
        return self.embeddings.embed_query(text)
