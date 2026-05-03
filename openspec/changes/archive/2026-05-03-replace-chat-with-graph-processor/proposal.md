## Why

The `ChatProcessor` is a legacy, stateless processor that only supports simple single-call LLM interactions. The `GraphProcessor` provides a more advanced, multi-step workflow (including intent checks and inquiry handling) using LangGraph. This change formalizes `GraphProcessor` as the primary processor for the application.

## What Changes

- **Finalize Replacement**: Officially replace `ChatProcessor` with `GraphProcessor` across the entire application.
- **Relocation**: Move `GraphProcessor` from `src/muggle/experimental/graph_processor.py` to `src/muggle/core/graph_processor.py`.
- **Cleanup**: Remove `ChatProcessor` from `src/muggle/core/processor.py` or remove the file if only `ProcessorInterface` remains (which should probably be moved to a more central location or kept in `core/__init__.py`).
- **Monitoring Update**: Update error messages in `src/muggle/blueprints/monitoring.py` to refer to "Processor" instead of "ChatProcessor".
- **Refactoring**: Update `src/muggle/app.py` to import `GraphProcessor` from its new location in `core`.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `llm-processor`: Update the spec to establish `GraphProcessor` as the standard implementation and clarify its graph-based requirements (intent check, inquiry handling).

## Impact

- **Breaking Change**: The `ChatProcessor` class will be removed.
- **Breaking Change**: `GraphProcessor` location will change from `experimental` to `core`.
- **UI/API**: No user-facing API changes expected, as `GraphProcessor` implements the same `ProcessorInterface`.
