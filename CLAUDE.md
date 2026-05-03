# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`muggle` is a RAG (Retrieval-Augmented Generation) chatbot built on LangGraph with Flask as the web layer. It answers insurance-related questions by retrieving relevant FAQ sections from a Milvus vector store and generating grounded responses via an LLM.

## Commands

```bash
poetry install                    # Install all dependencies
poetry run muggle                 # Start Flask dev server (config.toml → server.port, default 5001)
poetry run load-faq --file aia_faq.md  # Ingest FAQ markdown into Milvus
poetry run pytest                 # Run all tests
poetry run pytest tests/test_rag.py    # Run a single test file
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
api/            Flask Blueprints — depends on core
core/           Domain logic: LangGraph nodes, state, ProcessorInterface — depends on infra
infra/          Config, ModelRegistry, PromptRegistry, VectorStoreManager — depends on shared
shared/         Constants, parse_frontmatter utility — no internal deps
```

### Request flow through the LangGraph pipeline

```
START → IntentCheck → (pass?) → Summarization → QueryRewrite → Retrieval → Inquiry → END
                   ↘ (fail?) → Unhandled → END
```

Each node is a callable class accepting `(state: WorkflowState, config: RunnableConfig) → dict`:

1. **IntentCheck** — Structured output (Pydantic `IntentCheckResult`) decides if the message is in-scope
2. **Summarization** — `langmem` `SummarizationNode` compresses conversation memory when it exceeds token limits
3. **QueryRewrite** — Structured output rewrites the user question into a vector-search-optimized query
4. **Retrieval** — Dual-vector search (content_vector + header_vector) over Milvus with DashScope rerank and relevance threshold filtering
5. **Inquiry** — Structured output generates the final response from retrieved context
6. **Unhandled** — Hardcoded rejection for out-of-scope queries

### State

`WorkflowState` (Pydantic model, `src/muggle/core/state.py:10`) is the single state object flowing through the graph. Key fields: `messages` (LangChain message list, annotated with `add_messages` reducer), `pass_intent_check`, `vector_store_query`, `retrieved_context`, `response`.

The graph uses `InMemorySaver` for checkpointing — conversation state persists by `thread_id` during the server lifetime but does not survive restarts.

### Registries

- **ModelRegistry** (`src/muggle/infra/registry/model.py`) — Wraps `langchain.init_chat_model`. Models are registered with an alias (provider + model_id + kwargs) and instantiated lazily on first access. The default alias is `STR_LLM_DEFAULT` (`"llm-default"`).
- **PromptRegistry** (`src/muggle/infra/registry/prompt.py`) — Loads Jinja2-templated Markdown files with YAML frontmatter from `muggle.infra.prompts` (or a configurable package path). Organized into `system/` and `user/` subdirectories. Cached after first load.
- **VectorStoreManager** (`src/muggle/infra/registry/vector.py`) — Milvus client with a dual-vector schema (header_vector + content_vector, both 1024-dim). Creates collection on init if it doesn't exist. Supports insert, upsert, and search with DashScope embeddings.

### Config

`ConfigManager` (`src/muggle/infra/config.py`) reads `config.toml` and loads `.env` via `python-dotenv`. A global singleton `cfg` is used throughout the codebase (not injected). Sections: `[llm]`, `[server]`, `[prompts]`, `[vector_store]`, `[rerank]`, `[memory]`.

### Pydantic conventions

All Pydantic models in this project use v2-style `Field(default_factory=...)` syntax. Type annotations use Python 3.10+ union syntax (`str | None`). No `Optional[...]`.

## Testing

Tests use `unittest` (stdlib, not pytest fixtures). There are 8 test files under `tests/`. The most comprehensive is `test_rag.py` which mocks all registries and the LLM to test the full GraphProcessor pipeline end-to-end.
