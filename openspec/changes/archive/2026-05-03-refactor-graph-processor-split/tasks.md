## 1. Extract shared state and helpers

- [x] 1.1 Create `src/muggle/core/state.py` — move `WorkflowState`, `ingest_router`, `simple_human_message`, `config_map` from `graph_processor.py`; remove from `graph_processor.py`

## 2. Create node sub-packages

- [x] 2.1 Create `src/muggle/core/guard/__init__.py`
- [x] 2.2 Create `src/muggle/core/guard/intent_check.py` — `IntentCheckNode` class and `IntentCheckResult` model, moved from `graph_processor.py`
- [x] 2.3 Create `src/muggle/core/guard/unhandled.py` — `UnhandledNode` class, moved from module-level `unhandled_response_node`
- [x] 2.4 Create `src/muggle/core/memory/__init__.py`
- [x] 2.5 Create `src/muggle/core/search/__init__.py`
- [x] 2.6 Create `src/muggle/core/search/query_rewrite.py` — `QueryRewriteNode` class and `QueryRewriteResult` model, moved from `graph_processor.py`
- [x] 2.7 Create `src/muggle/core/search/retrieval.py` — `RetrievalNode` class, moved from `graph_processor.py` closure
- [x] 2.8 Create `src/muggle/core/response/__init__.py`
- [x] 2.9 Create `src/muggle/core/response/inquiry.py` — `InquiryNode` class and `InquiryResult` model, moved from `graph_processor.py`

## 3. Rewrite GraphProcessor

- [x] 3.1 Rewrite `graph_processor.py` — remove all node closures, result models, module-level helpers; inject node instances and assemble graph declaratively

## 4. Update exports and imports

- [x] 4.1 Update `src/muggle/core/__init__.py` — re-export `GraphProcessor` and new public symbols
- [x] 4.2 Update `tests/test_llm.py` — update imports to reflect new module locations for `IntentCheckResult`, `InquiryResult`, `QueryRewriteResult`

## 5. Verification

- [x] 5.1 Run existing test suite (`poetry run pytest`) — all tests must pass with no behavioral changes
- [x] 5.2 Verify `poetry run muggle` starts without errors
