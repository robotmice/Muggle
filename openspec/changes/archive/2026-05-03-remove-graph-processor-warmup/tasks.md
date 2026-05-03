## 1. Core removal

- [x] 1.1 Remove `warm_up()`, `is_initialized()`, `last_error` property, `_ready`, and `_last_error` from `src/muggle/core/graph_processor.py`
- [x] 1.2 Remove the `try: processor.warm_up() except: log` block from `src/muggle/app.py`
- [x] 1.3 Simplify `/health` in `src/muggle/blueprints/monitoring.py` — remove `is_initialized()` check and `last_error` reference, keep only processor presence check

## 2. Test cleanup

- [x] 2.1 Remove `processor.warm_up()` call from `tests/test_llm.py`
- [x] 2.2 Remove `processor.warm_up()` call from `tests/test_rag.py`

## 3. Verification

- [x] 3.1 Run `poetry run pytest` — all tests must pass
- [x] 3.2 Verify `ProcessorInterface` ABC remains unchanged
