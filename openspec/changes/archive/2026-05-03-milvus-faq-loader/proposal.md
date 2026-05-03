## Why

To enhance the chatbot's knowledge base with specific domain information from the American Institute of Architects (AIA). Currently, the application lacks a persistent vector store for retrieving contextually relevant information from unstructured documents like `aia_faq.md`. Implementing a Milvus-based vector store and a dedicated loader will establish the foundation for future Retrieval-Augmented Generation (RAG) capabilities.

## What Changes

- Implement a Milvus vector store configuration and connection utility.
- Create a document loading script to parse `aia_faq.md` and ingest its content into Milvus using a dual-vector schema.
- Implement a multi-level ingestion strategy storing both full FAQ sections and granular segments for large entries.

## Capabilities

### New Capabilities
- `vector-store`: Provides an interface for connecting to and interacting with a Milvus vector database, including collection creation and similarity search supporting dual vector fields (`header_vector` and `content_vector`).
- `faq-loader`: Handles the ingestion of FAQ data from `aia_faq.md` into the vector store, including text splitting, conditional chunking, and dual embedding generation.

### Modified Capabilities
<!-- No modified capabilities in this change. -->

## Impact

- **Infrastructure**: Requires a running Milvus instance (or access to one).
- **Dependencies**: Adds `pymilvus` and potentially additional LangChain document loader dependencies.
