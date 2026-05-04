# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`muggle` is a RAG (Retrieval-Augmented Generation) chatbot built on LangGraph with Flask as the web layer. It answers insurance-related questions by retrieving relevant FAQ sections and legal articles from a Milvus vector store and generating grounded responses via an LLM.

## Commands

```bash
poetry install                          # Install all dependencies
poetry run muggle                       # Start Flask dev server (config.toml → server.port, default 5001)
poetry run load-faq --file aia_faq.md --lang en-US # Ingest FAQ markdown into Milvus (collection: aia_faq)
poetry run load-law --file 中华人民共和国社会保险法.md --lang zh-CN # Ingest law markdown into Milvus (collection: social_insurance_law)
poetry run pytest                       # Run all tests
poetry run pytest tests/test_rag.py     # Run a single test file
poetry run python eval_retrieval.py                  # Label-driven retrieval eval (P@k, MRR, nDCG)
poetry run python eval_retrieval_ragas.py            # Ragas LLM-as-judge retrieval eval
poetry run python eval_retrieval.py --generate-sample  # Generate sample evaluation dataset
```

## Environment Variables

Copy `.env.example` to `.env` and populate:

- `DEEPSEEK_API_KEY` — LLM provider API key
- `DASHSCOPE_API_KEY` — Embedding + rerank API key
- `MILVUSAI_DASHSCOPE_API_KEY` — DashScope key for Milvus
- `MILVUS_URI` — Milvus server URI (e.g., Zilliz Cloud)
- `MILVUS_TOKEN` — Milvus auth token

## Architecture

### Dependency layering (top → bottom)

```
blueprints/     Flask Blueprints — depends on core
core/           Domain logic: LangGraph nodes, state, ProcessorInterface — depends on infra
infra/          Config, ModelRegistry, PromptRegistry, VectorStoreManager, loaders — depends on shared
shared/         Constants, parse_frontmatter utility — no internal deps
```

### Request flow through the LangGraph pipeline

```
START → IntentCheck → (pass?) → Summarization → QueryRewrite → Retrieval → Inquiry → Validation → END
                   ↘ (fail?) → Fallback → END

Validation retry loop:
  - pass → END
  - fail, attempts < max → Summarization (retry)
  - fail, attempts ≥ max → Fallback → END
```

Each node is a callable class accepting `(state: WorkflowState, config: RunnableConfig) → dict`:

1. **IntentCheck** — Structured output (Pydantic `IntentCheckResult`) decides if the message is in-scope
2. **Summarization** — `langmem` `SummarizationNode` compresses conversation memory when it exceeds token limits
3. **QueryRewrite** — Structured output rewrites the user question into dual-language search queries (zh-CN + en-US)
4. **Retrieval** — Hybrid search (dense content_vector + header_vector + BM25 sparse_vector, fused via RRF) across multiple collections (FAQ + Law), with DashScope rerank and relevance threshold filtering
5. **Inquiry** — Structured output generates the final response from retrieved context
6. **Validation** — Structured output (`ValidationResult`) scores the response quality; routes to retry, fallback, or end
7. **Fallback** — Hardcoded rejection for out-of-scope or failed queries

### State

`WorkflowState` (Pydantic model, `src/muggle/core/state.py`) is the single state object flowing through the graph. Key fields: `messages` (LangChain message list, annotated with `add_messages` reducer), `pass_intent_check`, `vector_store_queries` (dict keyed by lang_tag, e.g. `{"zh-CN": "...", "en-US": "..."}`), `retrieved_context`, `response`, `attempt_count`, `pass_validation`.

The graph uses `InMemorySaver` for checkpointing — conversation state persists by `thread_id` during the server lifetime but does not survive restarts.

### Registries

- **ModelRegistry** (`src/muggle/infra/registry/model.py`) — Wraps `langchain.init_chat_model`. Models are registered with an alias (provider + model_id + kwargs) and instantiated lazily on first access. The default alias is `STR_LLM_DEFAULT` (`"llm-default"`).
- **PromptRegistry** (`src/muggle/infra/registry/prompt.py`) — Loads Jinja2-templated Markdown files with YAML frontmatter from `muggle.infra.prompts` (or a configurable package path). Organized into `system/` and `user/` subdirectories. Cached after first load.
- **VectorStoreManager** (`src/muggle/infra/registry/vector.py`) — Milvus client with a dual-vector + sparse schema (header_vector + content_vector, both 1024-dim; sparse_vector via BM25 function). Creates collection on init if it doesn't exist. Supports `insert`, `upsert`, `search` (dense-only), and `hybrid_search` (dense + sparse fused with RRF).

### Config

`ConfigManager` (`src/muggle/infra/config.py`) reads `config.toml` and loads `.env` via `python-dotenv`. A global singleton `cfg` is used throughout the codebase (not injected). Sections: `[llm]`, `[server]`, `[prompts]`, `[vector_store]`, `[rerank]`, `[memory]`, `[validate]`, `[hybrid_search]`.

### Logging

Structured JSON-line logging via `muggle.infra.logging_setup.JsonFormatter`. Context variables `request_id_var` and `thread_id_var` are set per-request and automatically attached to log records. Individual nodes log duration via `log_duration()` helper.

### Query Cache

`QueryCache` (`src/muggle/infra/cache.py`) is an in-memory exact-match cache with TTL and LRU eviction. Cache keys are MD5-normalized (lowercased, stripped) query strings. Thread-safe. Not persistent.

### Multi-collection retrieval

The application initializes two `VectorStoreManager` instances — one for FAQ (`aia_faq`) and one for law (`social_insurance_law`). The `RetrievalNode` iterates over both collections, searching each with the appropriate `lang_tag` filter. Results are deduplicated by ID before reranking.

### Pydantic conventions

All Pydantic models in this project use v2-style `Field(default_factory=...)` syntax. Type annotations use Python 3.10+ union syntax (`str | None`). No `Optional[...]`.

## Testing

Tests use `unittest` (stdlib, not pytest fixtures). There are 11 test files under `tests/`. The most comprehensive is `test_rag.py` which mocks all registries and the LLM to test the full GraphProcessor pipeline end-to-end.

Evaluation scripts (`eval_retrieval.py`, `eval_retrieval_ragas.py`) live at the project root and are not part of the test suite — they connect to live Milvus and (for the Ragas variant) a live LLM.
