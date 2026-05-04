## 1. Config and Infrastructure

- [x] 1.1 Add `law_collection_name = "social_insurance_law"` to `[vector_store]` in `config.toml`
- [x] 1.2 Add `law_collection_name` to `ConfigManager.get_vector_store_params()` return dict

## 2. VectorStoreManager Parameterization

- [x] 2.1 Add optional `collection_name` parameter to `VectorStoreManager.__init__` (defaults to config value when `None`)
- [x] 2.2 Verify existing tests pass with the parameterized constructor

## 3. LawLoader

- [x] 3.1 Create `src/muggle/infra/loaders/law_loader.py` with `LawLoader` class
- [x] 3.2 Implement chapter splitting on `##` headers, filtering out TOC and source line
- [x] 3.3 Implement article splitting on `**第X条**` within each chapter
- [x] 3.4 Build chapter-prefixed headers (e.g., "工伤保险 — 第三十六条")
- [x] 3.5 Implement dual-vector embedding (header_vector + content_vector) per article
- [x] 3.6 Implement multi-level ingestion: full article + segments (>200 chars)
- [x] 3.7 Implement `run_loader()` CLI function with `--file` and `--lang` arguments

## 4. CLI Entry Point

- [x] 4.1 Add `load-law = "muggle.infra.loaders.law_loader:run_loader"` to `[project.scripts]` in `pyproject.toml`

## 5. Multi-Collection Retrieval

- [x] 5.1 Change `RetrievalNode.__init__` signature from `vector_store: VectorStoreManager` to `vector_stores: list[VectorStoreManager]`
- [x] 5.2 Update `RetrievalNode.__call__` to iterate all vector stores and merge results

## 6. Wiring

- [x] 6.1 Update `GraphProcessor.__init__` to accept `vector_stores: list[VectorStoreManager]`
- [x] 6.2 Update `app.py` `setup_components()` to create second `VectorStoreManager` for the law collection and pass list to `GraphProcessor`

## 7. Tests

- [x] 7.1 Update `RetrievalNode` tests for multi-collection signature
- [x] 7.2 Add `LawLoader` tests for chapter-article parsing and record generation
