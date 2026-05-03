## Context

The `muggle` application currently processes user messages using an LLM but lacks access to domain-specific knowledge. To improve the accuracy of responses regarding AIA (American Institute of Architects) programs and membership, we need to implement a Retrieval-Augmented Generation (RAG) pipeline. This change focuses on the **infrastructure and ingestion** phase: setting up a Milvus vector store and a mechanism to ingest FAQ data from `aia_faq.md`.

To maximize retrieval coverage and precision, we will implement a multi-level ingestion strategy that stores both full sections and, where necessary, granular segments, using a dual-vector schema.

## Goals / Non-Goals

**Goals:**
- Provide a robust interface for Milvus vector store operations supporting multiple vector fields.
- Implement a script to load and index `aia_faq.md` into Milvus.
- Implement a multi-level ingestion strategy:
    - **Always** store the full H3 section (Heading + Body).
    - **Additionally**, if > 200 chars, store segments (Heading + Body Segment).
- Ensure configuration is manageable via `config.toml` and `.env`.

**Non-Goals:**
- **Integrating retrieval into the `ChatProcessor` (out of scope for this change).**
- Implementing a generic multi-document ingestion system.
- Real-time synchronization of the vector store.

## Decisions

### 1. Vector Store Implementation: PyMilvus (Direct)
- **Choice**: Use `pymilvus` directly.
- **Rationale**: Support for a dual-vector schema (`header_vector` and `content_vector`) within a single record efficiently.

### 2. FAQ Parsing and Ingestion Strategy
- **Choice**: Multi-level ingestion using `MarkdownHeaderTextSplitter` and `RecursiveCharacterTextSplitter`.
- **Rationale**: 
    - Every logical FAQ section (H3) is important as a single unit. We will always create a record for the full Heading + Body.
    - For sections exceeding 200 characters, we add more granular records by chunking the body and prepending the heading.
    - This strategy ensures the retriever can find either the full context or a specific relevant segment in future implementation.

### 3. Embeddings: DashScope (Aliyun)
- **Choice**: Use `langchain_community.embeddings.DashScopeEmbeddings`.
- **Rationale**: Preferred provider in the current environment.

### 4. Configuration: New `[vector_store]` section in `config.toml`
- **Choice**: Add configuration for collection name, embedding model, and connection details.

## Risks / Trade-offs

- **[Risk] Schema Divergence** → **Mitigation**: By using `pymilvus` directly, we ensure the schema is exactly as required for dual-vector matching, even if standard LangChain wrappers are not used.
- **[Trade-off] Increased Storage** → Storing both full sections and segments increases the number of records, but for a typical FAQ document, the overhead is negligible compared to the retrieval benefits.
