# Capability: bm25-sparse-vector

## Purpose
Enables BM25 sparse vector generation on the FAQ collection for keyword-based retrieval, and a hybrid search API combining dense and sparse retrieval with RRF fusion.

## Requirements

### Requirement: BM25 Sparse Vector Generation
The system SHALL enable BM25 sparse vector generation on the FAQ collection so that the `text` field is automatically converted into a `SPARSE_FLOAT_VECTOR` for keyword-based retrieval.

#### Scenario: BM25 function registered on collection
- **WHEN** the collection is created via `VectorStoreManager._initialize_collection()`
- **THEN** the schema MUST include a `sparse_vector` field of type `SPARSE_FLOAT_VECTOR`
- **AND** a BM25 Function MUST be registered that maps `text` → `sparse_vector`
- **AND** the `text` field MUST have `enable_analyzer=True` for BM25 tokenization

#### Scenario: Sparse vector auto-generated on insert
- **WHEN** a record with a `text` field is inserted or upserted
- **THEN** Milvus automatically computes the `sparse_vector` via the BM25 Function
- **AND** no external embedding call is required

### Requirement: Hybrid Search API
The system SHALL provide a hybrid search method that combines dense vector search (content_vector, header_vector) with sparse vector search (BM25) in a single Milvus call.

#### Scenario: Hybrid search with RRF fusion
- **WHEN** `VectorStoreManager.hybrid_search(query_text, limit)` is called
- **THEN** it performs a hybrid search across `content_vector`, `header_vector`, and `sparse_vector` fields
- **AND** it fuses the three result sets using RRF (Reciprocal Rank Fusion)
- **AND** it returns the top `limit` merged results

#### Scenario: RRF configurable parameter
- **WHEN** the hybrid search is configured
- **THEN** the RRF `k` parameter SHALL be read from `config.toml` under `[hybrid_search].rrf_k`
- **AND** if not configured, it defaults to 60
