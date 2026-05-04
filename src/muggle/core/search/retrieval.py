from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from muggle.core.state import WorkflowState
from muggle.infra.registry import VectorStoreManager


class RetrievalNode:
    def __init__(self, vector_stores: list[VectorStoreManager], reranker: DashScopeRerank,
                 recall_limit: int, relevance_threshold: float):
        self.vector_stores = vector_stores
        self.reranker = reranker
        self.recall_limit = recall_limit
        self.relevance_threshold = relevance_threshold

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        queries = state.vector_store_queries
        if not queries:
            return {"retrieved_context": []}

        results = []
        seen_ids: set[str] = set()
        for lang_tag, query in queries.items():
            for vs in self.vector_stores:
                lang_results = vs.hybrid_search(
                    query_text=query,
                    limit=self.recall_limit,
                    filter=f'lang_tag == "{lang_tag}"',
                )
                for res in lang_results:
                    res_id = res.get("id", "")
                    if res_id not in seen_ids:
                        seen_ids.add(res_id)
                        results.append(res)

        if not results:
            return {"retrieved_context": []}

        docs = [
            Document(
                page_content=res.get("text", ""),
                metadata={"header": res.get("header", ""), "is_segment": res.get("is_segment", False)}
            )
            for res in results
        ]

        rerank_query = queries.get("zh-CN") or queries.get("en-US")
        reranked_docs = self.reranker.compress_documents(documents=docs, query=rerank_query)

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
