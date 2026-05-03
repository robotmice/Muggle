from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from muggle.core.state import WorkflowState
from muggle.infra.registry import VectorStoreManager


class RetrievalNode:
    def __init__(self, vector_store: VectorStoreManager, reranker: DashScopeRerank,
                 recall_limit: int, relevance_threshold: float):
        self.vector_store = vector_store
        self.reranker = reranker
        self.recall_limit = recall_limit
        self.relevance_threshold = relevance_threshold

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        query = state.vector_store_query
        if not query:
            return {"retrieved_context": []}

        results = self.vector_store.search(query_text=query, vector_field="content_vector", limit=self.recall_limit)
        results += self.vector_store.search(query_text=query, vector_field="header_vector", limit=self.recall_limit)
        if not results:
            return {"retrieved_context": []}

        docs = [
            Document(
                page_content=res.get("text", ""),
                metadata={"header": res.get("header", ""), "is_segment": res.get("is_segment", False)}
            )
            for res in results
        ]

        reranked_docs = self.reranker.compress_documents(documents=docs, query=query)

        final_context = []
        for doc in reranked_docs:
            score = doc.metadata.get("relevance_score", 0.0)
            if score >= self.relevance_threshold:
                final_context.append({
                    "text": doc.page_content,
                    "header": doc.metadata.get("header", ""),
                    "is_segment": doc.metadata.get("is_segment", False),
                    "relevance_score": score
                })

        return {"retrieved_context": final_context}
