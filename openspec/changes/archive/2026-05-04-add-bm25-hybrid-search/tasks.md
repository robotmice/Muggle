## 1. Configuration

- [x] 1.1 Add `[hybrid_search]` section to `config.toml` with `rrf_k = 60` and `recall_limit_per_route = 15`
- [x] 1.2 Add `get_hybrid_search_params()` method to `ConfigManager` in `src/muggle/infra/config.py`

## 2. Schema Migration

- [x] 2.1 Add `sparse_vector` field (SPARSE_FLOAT_VECTOR) and `lang_tag` field (VARCHAR(64)) to collection schema in `VectorStoreManager._initialize_collection()`
- [x] 2.2 Register BM25 Function mapping `text` → `sparse_vector` during collection creation
- [x] 2.3 Add index for `sparse_vector` field (SPARSE_INVERTED_INDEX with BM25 metric)

## 3. Hybrid Search API

- [x] 3.1 Add `hybrid_search(query_text, limit)` method to `VectorStoreManager` in `src/muggle/infra/registry/vector.py`
- [x] 3.2 Implement hybrid search with three routes (content_vector, header_vector, sparse_vector) and RRF fusion via Milvus API

## 4. Query Rewrite Update

- [x] 4.1 Update `QueryRewriteResult` to output `query_zh` and `query_en` fields instead of single `vector_store_query`
- [x] 4.2 Update `QueryRewriteNode` to return `{"vector_store_queries": {"zh-CN": ..., "en-US": ...}}`
- [x] 4.3 Update `WorkflowState.vector_store_query` to `vector_store_queries: dict[str, str]`

## 5. Retrieval Node Update

- [x] 5.1 Update `RetrievalNode.__call__` to iterate over `vector_store_queries`, searching with `lang_tag` filter per language
- [x] 5.2 Merge and deduplicate results from both language searches by `id`
- [x] 5.3 Use `hybrid_search()` instead of two separate `search()` calls (per the BM25 hybrid search change)
- [x] 5.4 Pass hybrid search config params to `RetrievalNode` via `GraphProcessor`

## 6. Tests

- [x] 6.1 Update `test_rag.py` mocks to cover dual-language `vector_store_queries` and `hybrid_search()`
- [x] 6.2 Add test for dual-language search deduplication by `id`

## 7. Verification

- [x] 7.1 Drop and re-create collection, then run `load-faq` to verify re-indexing produces sparse vectors with lang_tag
- [x] 7.2 Manual smoke test: send queries and verify cross-language retrieval results
