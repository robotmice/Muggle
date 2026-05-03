# Capability: vector-store

## Purpose
Manages connections to the Milvus vector database and defines schemas for storing and searching multi-vector embeddings.

## Requirements

### Requirement: Milvus Connection Management
The system SHALL provide a centralized utility to establish and manage connections to a Milvus instance using parameters defined in the application configuration.

#### Scenario: Successful connection
- **WHEN** the `VectorStore` is initialized
- **THEN** it successfully connects to the configured Milvus host and port.

### Requirement: FAQ Collection Management with Dual Vectors
The system SHALL define and maintain a Milvus collection specifically for FAQ data, with a schema that includes two distinct vector fields:
1. `header_vector`: Embedding of the question heading (H3).
2. `content_vector`: Embedding of the combined question heading and body.

#### Scenario: Collection initialization with dual vectors
- **WHEN** the system starts and the FAQ collection does not exist
- **THEN** it creates the collection with the schema including `header_vector`, `content_vector`, and metadata fields.

### Requirement: Multi-Vector Similarity Search
The system SHALL provide an interface to perform vector similarity searches against either the `header_vector` or `content_vector` fields, or both, depending on the retrieval strategy.

#### Scenario: Search by header
- **WHEN** a query is performed against the `header_vector` field
- **THEN** it returns documents ranked by the similarity of the query to the question headings.
