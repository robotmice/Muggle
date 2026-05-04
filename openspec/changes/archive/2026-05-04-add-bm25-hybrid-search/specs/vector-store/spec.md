## MODIFIED Requirements

### Requirement: FAQ Collection Management with Dual Vectors
The system SHALL define and maintain a Milvus collection specifically for FAQ data, with a schema that includes:
1. `header_vector`: Embedding of the question heading (H3), FLOAT_VECTOR dim=1024.
2. `content_vector`: Embedding of the combined question heading and body, FLOAT_VECTOR dim=1024.
3. `sparse_vector`: BM25 sparse vector auto-generated from the `text` field, SPARSE_FLOAT_VECTOR.
4. `lang_tag`: Language tag for the FAQ content, VARCHAR(64). Supported values: `zh-CN`, `en-US`.

#### Scenario: Collection initialization with hybrid schema
- **WHEN** the system starts and the FAQ collection does not exist
- **THEN** it creates the collection with the schema including `header_vector`, `content_vector`, `sparse_vector`, `lang_tag`, and metadata fields
- **AND** a BM25 Function is registered on the `text` field to auto-populate `sparse_vector`

### Requirement: Multi-Vector Similarity Search
The system SHALL provide an interface to perform vector similarity searches against dense vector fields (`header_vector`, `content_vector`) and a hybrid search interface that combines dense and sparse (BM25) retrieval with RRF fusion.

#### Scenario: Dense search by header
- **WHEN** a query is performed against the `header_vector` field via `search()`
- **THEN** it returns documents ranked by the similarity of the query to the question headings.

#### Scenario: Hybrid search with dense and sparse
- **WHEN** a query is performed via `hybrid_search()`
- **THEN** it combines results from `header_vector`, `content_vector`, and `sparse_vector` using RRF fusion
- **AND** returns the top N merged documents
