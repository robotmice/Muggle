import logging
import os
from typing import List, Dict, Any, Optional
from pymilvus import MilvusClient, DataType, Function, FunctionType
from langchain_community.embeddings import DashScopeEmbeddings
from muggle.infra.config import cfg

logger = logging.getLogger(__name__)


class VectorStoreManager:
    def __init__(self, collection_name: str | None = None):
        params = cfg.get_vector_store_params()
        self.uri = params["uri"]
        self.token = params["token"]
        self.collection_name = collection_name or params["collection_name"]
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
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2048, enable_analyzer=True)
        schema.add_field(field_name="header", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="is_segment", datatype=DataType.BOOL)
        schema.add_field(field_name="lang_tag", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)

        schema.add_function(
            Function(
                name="bm25",
                function_type=FunctionType.BM25,
                input_field_names=["text"],
                output_field_names=["sparse_vector"],
            )
        )

        # In managed environments like Zilliz, AUTOINDEX often outperforms manual HNSW configurations.
        # Benchmarks show it can achieve significantly higher Queries Per Second (QPS) because it applies advanced optimizations like:
        # * SIMD Acceleration: Uses CPU-level instructions for faster math.
        # * Dynamic Quantization: Automatically compresses vectors to reduce memory overhead without sacrificing much accuracy.
        # * Better Filtering: While standard HNSW can struggle with metadata filtering, AUTOINDEX often handles hybrid searches (vector + scalar filters) more efficiently.

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
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="BM25"
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
            output_fields=["id", "text", "header", "is_segment", "lang_tag"]
        )
        # Flatten results
        return [res["entity"] for res in results[0]] if results else []

    def hybrid_search(self, query_text: str, limit: int | None = None,
                      filter: str = "") -> List[Dict[str, Any]]:
        """Perform hybrid search combining dense (content + header) and sparse (BM25) retrieval."""
        from pymilvus import AnnSearchRequest, RRFRanker

        query_vector = self.embeddings.embed_query(query_text)
        hs_params = cfg.get_hybrid_search_params()
        rrf_k = hs_params["rrf_k"]
        recall_limit = hs_params["recall_limit_per_route"]
        final_limit = limit if limit is not None else self.top_k

        content_req = AnnSearchRequest(
            data=[query_vector],
            anns_field="content_vector",
            param={},
            limit=recall_limit,
            expr=filter if filter else None,
        )
        header_req = AnnSearchRequest(
            data=[query_vector],
            anns_field="header_vector",
            param={},
            limit=recall_limit,
            expr=filter if filter else None,
        )
        sparse_req = AnnSearchRequest(
            data=[query_text],
            anns_field="sparse_vector",
            param={},
            limit=recall_limit,
            expr=filter if filter else None,
        )

        results = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[content_req, header_req, sparse_req],
            ranker=RRFRanker(k=rrf_k),
            limit=final_limit,
            output_fields=["id", "text", "header", "is_segment", "lang_tag"],
        )
        return [res["entity"] for res in results[0]] if results else []

    def embed_text(self, text: str) -> List[float]:
        """Utility to embed a single text string."""
        return self.embeddings.embed_query(text)
