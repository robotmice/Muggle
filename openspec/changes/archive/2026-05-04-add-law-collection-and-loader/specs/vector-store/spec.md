## MODIFIED Requirements

### Requirement: FAQ Collection Management with Dual Vectors

The system SHALL define and maintain Milvus collections for document data. `VectorStoreManager` SHALL accept an optional `collection_name` parameter; when omitted, it SHALL use the configured default collection name. Each collection SHALL use a schema that includes:
1. `header_vector`: Embedding of the section heading, FLOAT_VECTOR dim=1024.
2. `content_vector`: Embedding of the combined heading and body, FLOAT_VECTOR dim=1024.
3. `sparse_vector`: BM25 sparse vector auto-generated from the `text` field, SPARSE_FLOAT_VECTOR.
4. `lang_tag`: Language tag for the content, VARCHAR(64). Supported values: `zh-CN`, `en-US`.

#### Scenario: Collection initialization with default name

- **WHEN** `VectorStoreManager` is initialized without a collection name
- **THEN** it uses the collection name from `config.toml` `[vector_store]` `collection_name`

#### Scenario: Collection initialization with explicit name

- **WHEN** `VectorStoreManager` is initialized with `collection_name="social_insurance_law"`
- **THEN** it creates and manages the collection named `social_insurance_law` with the same dual-vector + BM25 schema

#### Scenario: Collection initialization with hybrid schema

- **WHEN** the system starts and a managed collection does not exist
- **THEN** it creates the collection with the schema including `header_vector`, `content_vector`, `sparse_vector`, `lang_tag`, and metadata fields
- **AND** a BM25 Function is registered on the `text` field to auto-populate `sparse_vector`
