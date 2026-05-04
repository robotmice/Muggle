## Context

The system currently has a single Milvus collection (`aia_faq`) populated by `FAQLoader`, which splits markdown on `###` headers (Q&A pairs). We need to add a second collection for the Social Insurance Law of the PRC, which has a different structure: chapters (`##`) containing articles (`**第X条**`). The law document is Chinese-only (`zh-CN`).

The same `VectorStoreManager` schema (dual dense vectors + BM25 sparse vector + lang_tag) applies to both collections. The retrieval path must search both collections and merge results.

## Goals / Non-Goals

**Goals:**
- Ingest the Social Insurance Law into a dedicated Milvus collection
- Search across both FAQ and law collections at query time
- Keep the `VectorStoreManager` API backward-compatible
- Reuse the existing Milvus schema, indexes, and BM25 function

**Non-Goals:**
- A generic multi-collection configuration framework (this is collection #2, not N)
- Query-time routing by document type (queries search both collections)
- Changes to the embedding model, reranker, or hybrid search algorithm
- A new Milvus connection or embedding client per collection

## Decisions

### D1: VectorStoreManager accepts optional collection_name

`__init__` gains `collection_name: str | None = None`. If `None`, it reads `cfg.get_vector_store_params()["collection_name"]` as before.

**Why not a `VectorStoreManagerFactory` or registry pattern?** Two instances is not enough to justify an abstraction. A single optional parameter is the minimum change.

**Why not create a second Milvus client?** The Milvus client is connection-pooled internally. Two `VectorStoreManager` instances sharing the same `uri`/`token` is fine — the overhead is one extra HTTP connection at most.

### D2: RetrievalNode iterates multiple vector stores

`RetrievalNode.__init__` changes signature from `vector_store: VectorStoreManager` to `vector_stores: list[VectorStoreManager]`. At search time, it loops over all stores and merges results before deduplication and reranking.

**Why merge before rerank?** Reranking is the bottleneck (cross-encoder). Merging first and reranking once is more efficient than reranking per-collection and then merging.

### D3: LawLoader splits on articles, prefixes chapter names

The document structure is:

```
## 第一章 总则
**第一条** 为了规范社会保险关系...
**第二条** 国家建立基本养老保险...

## 第二章 基本养老保险
**第十条** 职工应当参加基本养老保险...
```

The loader:
1. Splits on `##` to get chapters, filtering out the TOC block (目录) and source line (来源)
2. Within each chapter, regex-splits on `\*\*第[一二三四五六七八九十百]+条\*\*` to extract articles
3. Builds `header = "{chapter_name} — {article_heading}"` (e.g., "基本养老保险 — 第十条")
4. `text = "{header}\n{article_body}"` for embedding

**Why article-level, not chapter-level?** Articles are self-contained legal provisions (one provision = one rule). Chapter-level chunks would be too large for precise retrieval.

**Why chapter prefix in header?** An article number like "第三十六条" is meaningless without knowing it belongs to the Work Injury Insurance chapter. The prefix makes retrieved results self-documenting.

### D4: Config addition

Add `law_collection_name = "social_insurance_law"` to `[vector_store]` in `config.toml`. `ConfigManager.get_vector_store_params()` gains `law_collection_name`. `app.py` reads it to create the second `VectorStoreManager`.

**Why config, not hardcoded in the loader?** The collection name is infrastructure configuration. Changing it should not require editing Python code. The loader itself doesn't care about the collection name — it receives a `VectorStoreManager` that already knows.

### D5: Same schema, same BM25 function

The law collection uses the identical schema as `aia_faq` — same vector dimensions, same field types, same BM25 function. This is intentional: the retrieval path treats both collections uniformly.

## Risks / Trade-offs

- **Two collections double the Milvus search latency** → Each collection search is independent and can be parallelized with `asyncio` in the future. For now, serial iteration is acceptable given the small collection count.
- **Same schema means both collections share the same `lang_tag` filter semantics** → The law is zh-CN only, so en-US queries will return no law results naturally. This is correct behavior.
- **If more document types are added, the list of VectorStoreManagers grows linearly** → At that point, extract a `MultiCollectionSearcher` or introduce collection metadata. Not needed yet.
