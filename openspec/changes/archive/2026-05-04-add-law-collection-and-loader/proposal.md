## Why

The system currently only ingests and searches AIA FAQ content. The Social Insurance Law of the PRC is a foundational legal document that users will ask questions about — questions the FAQ alone cannot answer. This document needs its own Milvus collection and a loader that understands its article-based structure.

## What Changes

- **New** `LawLoader` that parses the law markdown by chapter and article, with chapter-name-prefixed headers for context
- **New** `load-law` CLI entry point for ingesting the law document
- **New** `law_collection_name` config field for the second Milvus collection
- **Modify** `VectorStoreManager` to accept an optional `collection_name` parameter (defaults to config value)
- **Modify** `RetrievalNode` to search across multiple `VectorStoreManager` instances and merge results
- **Modify** `GraphProcessor` and `app.py` to wire multiple vector stores into the retrieval pipeline

## Capabilities

### New Capabilities
- `law-loader`: Parses the Social Insurance Law markdown (chapters + articles) and ingests into a dedicated Milvus collection with dual-vector embeddings and BM25 sparse vectors

### Modified Capabilities
- `vector-store`: `VectorStoreManager` SHALL accept an optional `collection_name` parameter to support multiple collections
- `faq-retrieval`: Retrieval SHALL search across all configured vector store collections and merge results before reranking
- `cli-entrypoint`: A new `load-law` Poetry script SHALL be registered for law document ingestion

## Impact

- `src/muggle/infra/registry/vector.py` — constructor parameter
- `src/muggle/infra/loaders/law_loader.py` — new file
- `src/muggle/infra/config.py` — new config accessor
- `src/muggle/core/search/retrieval.py` — multi-collection iteration
- `src/muggle/core/graph_processor.py` — accepts list of vector stores
- `src/muggle/app.py` — creates two VectorStoreManager instances
- `config.toml` — new `law_collection_name` field
- `pyproject.toml` — new `load-law` script entry
