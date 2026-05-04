## MODIFIED Requirements

### Requirement: FAQ Similarity Search

The system SHALL support retrieving relevant content using hybrid search that combines dense vector similarity with BM25 sparse vector keyword matching across multiple languages and across all configured vector store collections.

#### Scenario: Hybrid retrieval with dense and sparse

- **WHEN** a query is sent to the retrieval system
- **THEN** it MUST use `VectorStoreManager.hybrid_search()` to perform a combined dense + sparse search with RRF fusion for each language-specific query
- **AND** it MUST search across ALL configured `VectorStoreManager` instances
- **AND** it MUST search zh-CN content with the zh-CN rewritten query and en-US content with the en-US rewritten query
- **AND** it MUST merge and deduplicate results from all collections and both language searches
- **AND** it MUST return the top N relevant entries (header, text, and lang_tag) from the merged results
- **AND** the retrieved results SHALL be passed through DashScopeRerank for cross-encoder refinement
- **AND** results with relevance_score below the configured threshold MUST be filtered out
