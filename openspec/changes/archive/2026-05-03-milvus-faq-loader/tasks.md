## 1. Configuration and Setup

- [x] 1.1 Add `[vector_store]` section to `config.toml` with `collection_name`, `embedding_model`, and connection parameters.
- [x] 1.2 Update `src/muggle/infra/config.py` to include a `get_vector_store_params()` method.
- [x] 1.3 Ensure `MILVUS_URI` and `MILVUS_TOKEN` are correctly handled in `.env`.

## 2. Infrastructure Implementation

- [x] 2.1 Create `src/muggle/infra/registry/vector.py` to manage Milvus connections and dual-vector collection initialization (using `pymilvus`).
- [x] 2.2 Implement a custom `VectorStoreManager` to handle schema definition, index creation, and raw ingestion for dual vectors.

## 3. FAQ Loader Implementation

- [x] 3.1 Create `src/muggle/infra/loaders/faq_loader.py`.
- [x] 3.2 Implement Markdown parsing logic to extract Header headers and their corresponding bodies.
- [x] 3.3 Implement the multi-level loading program:
    - For EVERY section: Generate embeddings for (Header) and (Header + Full Body) and store as record #1.
    - If Header + Full Body > 200 chars:
        - Split body using `RecursiveCharacterTextSplitter` (20 overlap).
        - Prepend Header to each segment.
        - For each segment: Generate embeddings for (Header) and (Header + Segment) and store as additional records.
- [x] 3.4 Add a CLI command or entry point to trigger the loading process.

## 4. Verification

- [x] 4.1 Run the FAQ loader and verify that both full sections and segments are populated in Milvus.
- [x] 4.2 Verify similarity search results when querying against different vector fields (header vs content).
- [x] 4.3 Add unit/integration tests for the custom dual-vector management, multi-level ingestion, and search utility.
