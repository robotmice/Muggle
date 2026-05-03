# Capability: faq-retrieval

## Purpose
Defines the logic for retrieving and formatting FAQ information from the vector store.

## Requirements

### Requirement: FAQ Similarity Search
The system SHALL support retrieving relevant FAQ sections from Milvus using similarity search.

#### Scenario: Relevant FAQ found
- **WHEN** a query is sent to the retrieval system
- **THEN** it MUST return the top N relevant FAQ entries (header and text) from Milvus
- **AND** it MUST use the configured embedding model for the query vector.

### Requirement: FAQ Context Formatting
The system SHALL format retrieved FAQ sections into a single context string suitable for inclusion in an LLM prompt.

#### Scenario: Context formatting
- **WHEN** multiple FAQ entries are retrieved
- **THEN** they MUST be concatenated with clear separators between header and text for each entry.
