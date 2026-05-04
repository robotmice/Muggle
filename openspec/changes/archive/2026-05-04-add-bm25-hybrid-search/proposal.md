## Why

Insurance terminology is highly specialized — clause numbers, legal citations, and domain jargon are common. Pure dense vector search lacks precision for exact keyword matching. BM25 sparse vector search naturally excels at tf-idf matching for rare terms, complementing existing dense semantic search to form a hybrid recall strategy that improves retrieval quality.

## What Changes

- Milvus collection schema adds a `sparse_vector` (SPARSE_FLOAT_VECTOR) field, auto-populated from the `text` field via a built-in BM25 Function
- `VectorStoreManager` gains a `hybrid_search()` method that performs dense (content_vector + header_vector) + sparse retrieval in a single call, using RRF fusion
- `RetrievalNode` switches from two independent dense searches to one hybrid search call
- DashScopeRerank remains as the cross-encoder refinement step after hybrid recall
- Config gains a new `[hybrid_search]` section (RRF k, recall limits)
- Existing collection must be re-indexed to activate sparse_vector

## Capabilities

### New Capabilities
- `bm25-sparse-vector`: Milvus BM25 Function auto-generates sparse vectors from text, enabling keyword-level exact-match search

### Modified Capabilities
- `vector-store`: schema adds sparse_vector field and BM25 Function; search API adds hybrid search path
- `faq-retrieval`: RetrievalNode switches from two dense searches to a single hybrid search, updating recall logic

## Impact

- **Schema**: collection gains new field; existing data requires re-index (can reuse `load-faq` command)
- **Config**: `config.toml` gains `[hybrid_search]` section
- **Deps**: requires Milvus 2.4+ (Zilliz Cloud already supported) with `SPARSE_FLOAT_VECTOR` and `BM25EmbeddingFunction`
- **Nodes**: `RetrievalNode` internal logic changes, interface unchanged (still returns `retrieved_context`)
