## Why

`GraphProcessor` carries `warm_up()`, `is_initialized()`, and `last_error` — a graceful-startup pattern that adds complexity without meaningful protection. The warm-up probe catches an unreachable LLM at startup instead of at first request, but the server still starts either way (the exception is caught and logged). This indirection persists through a health endpoint that checks `is_initialized()` rather than simply verifying the processor exists. Removing this machinery simplifies the processor to a plain constructor and the health endpoint to a single existence check.

## What Changes

- Remove `warm_up()`, `is_initialized()`, `last_error` property, and internal `_ready`/`_last_error` fields from `GraphProcessor`
- Remove the `try: processor.warm_up() except: log` block from `app.py`
- Simplify `/health` endpoint to return 200 if processor exists on app context, 503 if not — no `is_initialized()` or `last_error` dependency
- Remove `warm_up()` calls from `test_llm.py` and `test_rag.py`

## Capabilities

### New Capabilities

None. This is purely removal.

### Modified Capabilities

- `application-lifecycle`: Remove the "Graceful Warm-up" requirement entirely. Modify "Health Monitoring" unhealthy scenario to trigger on missing processor (not uninitialized processor).
- `llm-processor`: Remove the "Robust Processor Initialization" requirement (warm-up validation scenario).

## Impact

- `src/muggle/core/graph_processor.py` — remove warm_up, is_initialized, last_error, _ready, _last_error
- `src/muggle/app.py` — remove warm_up try/except block
- `src/muggle/blueprints/monitoring.py` — remove is_initialized/last_error check
- `tests/test_llm.py`, `tests/test_rag.py` — remove warm_up() calls
