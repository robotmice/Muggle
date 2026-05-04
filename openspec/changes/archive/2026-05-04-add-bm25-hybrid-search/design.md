## Context

The current retrieval architecture uses two independent dense searches (content_vector + header_vector), both relying on DashScope embedding cosine similarity. Insurance FAQ content contains many clause numbers, legal citations, and domain-specific terminology that dense embeddings do not cover well semantically.

Milvus 2.4+ includes a built-in BM25 Embedding Function that can generate `SPARSE_FLOAT_VECTOR` directly from a `text` field, with no external service needed. The hybrid search API supports combining dense + sparse retrieval in a single call, with native RRF / WeightedRanker fusion.

## Goals / Non-Goals

**Goals:**
- Enable BM25 sparse vectors in the Milvus collection, coexisting with existing dense vectors
- `VectorStoreManager` provides a `hybrid_search()` method combining dense + sparse retrieval in one call
- `RetrievalNode` uses hybrid search instead of two independent dense searches
- RRF as the default fusion strategy — works without parameter tuning
- DashScopeRerank retained — hybrid expands recall, cross-encoder ensures precision

**Non-Goals:**
- Do not replace DashScope embedding (dense remains as one route)
- Do not introduce an external BM25 service (use Milvus built-in Function)
- Do not change `RetrievalNode`'s external state interface (still returns `retrieved_context`)
- Do not optimize the FAQ ingestion pipeline (schema-level adaptation only)
- `lang_tag` field added to schema and ingestion as a language tag (default `zh-CN`)

## Decisions

### 1. Fusion Strategy: RRF First

**Choice**: RRF (Reciprocal Rank Fusion)
**Alternative**: WeightedRanker

Rationale: BM25 scores and cosine similarity operate on different scales; WeightedRanker requires careful tuning to be effective. RRF is rank-based, naturally scale-agnostic, and works out of the box. If scenario-specific weighting is needed later, WeightedRanker can be introduced then.

### 2. BM25 Generation: Milvus Built-in Function

**Choice**: Define a `BM25EmbeddingFunction` in the collection schema; Milvus auto-computes `sparse_vector` from the `text` field on insert/upsert
**Alternative**: External sparse embedding generation (e.g., via DashScope or another model)

Rationale: Zero extra dependencies, zero network calls, fully handled server-side by Milvus. Minimal intrusion to existing ingestion code.

### 3. Number of Hybrid Routes

**Choice**: Three routes — content_vector (dense) + header_vector (dense) + sparse_vector (BM25)
**Alternative**: Two routes — content_vector (dense) + sparse_vector (BM25), dropping header_vector

Header and content occupy different semantic spaces (question heading vs. answer body). Dense search on both remains valuable. RRF fuses three routes with no added complexity.

### 6. Dual-Language Query Rewrite

**Choice**: `QueryRewriteNode` returns separate rewritten queries for zh-CN and en-US. `RetrievalNode` runs independent searches per language (filtering by `lang_tag`), then merges and deduplicates by `id`.

**Alternative**: Single query with no lang_tag filter — searches all content regardless of language.

Rationale: Each query is optimized for its target language's vocabulary and BM25 tokenization. Searching zh-CN content with the zh-CN query and en-US content with the en-US query maximizes relevance for both languages. Deduplication by `id` prevents the same FAQ section from appearing twice if retrieved by both language searches.

### 4. Search API Design

**Choice**: Add a new `hybrid_search(query_text, limit)` method on `VectorStoreManager` that calls the Milvus hybrid search API internally
**Alternative**: Modify the existing `search()` method parameters

A separate method clearly expresses the different semantics and avoids breaking existing `search()` callers.

### 5. Config Parameters

New `[hybrid_search]` config section:
```
[hybrid_search]
rrf_k = 60                     # RRF smoothing parameter
recall_limit_per_route = 15    # Recall limit per route
```

## Risks / Trade-offs

- **[Schema migration] Existing collection must be dropped and re-created** → Re-run `load-faq` to re-ingest; data volume is small (FAQ document), risk is manageable
- **[Milvus version] BM25 Function requires Milvus 2.4+** → Zilliz Cloud defaults to ≥2.4; local dev needs version confirmation
- **[Performance] One extra sparse search adds latency** → BM25 search is highly optimized in Milvus, adds ~5-10ms, within acceptable range
- **[Cold start] RRF weights cannot be tuned for the insurance domain yet** → Launch first, observe results, collect data, then decide whether to introduce weighted strategy
