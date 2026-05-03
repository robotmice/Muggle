## 1. Config plumbing

- [x] 1.1 Add `max_attempts = 5` to `[validate]` section in `config.toml`
- [x] 1.2 Add `max_attempts` to `get_validate_params()` in `src/muggle/infra/config.py`

## 2. Constant renames

- [x] 2.1 Rename `STR_NODE_SUMMARIZE` → `STR_NODE_SUMMARIZATION`, `STR_NODE_VALIDATE` → `STR_NODE_VALIDATION`, `STR_NODE_UNHANDLED` → `STR_NODE_FALLBACK` in `src/muggle/shared/constants.py`
- [x] 2.2 Rename `STR_PROMPT_VALIDATE` → `STR_PROMPT_VALIDATION` in `src/muggle/shared/constants.py`

## 3. State field and router

- [x] 3.1 Rename `retry_count` → `attempt_count` in `WorkflowState` (field definition + default) in `src/muggle/core/state.py`
- [x] 3.2 Convert `validation_router` function to `ValidationRouter` class accepting `max_attempts` in `src/muggle/core/state.py`
- [x] 3.3 Update `intent_check.py` to return `attempt_count: 0` instead of `retry_count: 0`
- [x] 3.4 Rename `retry_count` → `attempt_count` in `ValidateNode.__call__` in `src/muggle/core/validate.py`

## 4. Node and file renames

- [x] 4.1 Rename `validate.py` → `validation.py`, rename `ValidateNode` → `ValidationNode`
- [x] 4.2 Rename `unhandled.py` → `fallback.py`, rename `UnhandledNode` → `FallbackNode`
- [x] 4.3 Rename `prompt-validate.md` → `prompt-validation.md`
- [x] 4.4 Update `__init__.py` exports in `src/muggle/core/guard/` for FallbackNode

## 5. Graph processor wiring

- [x] 5.1 Update all imports in `graph_processor.py` (new names, new paths, ValidationRouter)
- [x] 5.2 Update conditional edges to use instantiated `ValidationRouter(max_attempts=...)`

## 6. Tests

- [x] 6.1 Rename `retry_count` → `attempt_count` and update router tests in `tests/test_validate.py`
- [x] 6.2 Update test method names referencing "retry" in `tests/test_validate.py`
- [x] 6.3 Run full test suite with `poetry run pytest`
