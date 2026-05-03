## Context

The application currently has two processor implementations: `ChatProcessor` (legacy, stateless) and `GraphProcessor` (modern, LangGraph-based). `GraphProcessor` is currently located in the `experimental` package but is already being used as the primary processor in `app.py`. This design formalizes the transition by promoting `GraphProcessor` to the `core` package and removing the legacy `ChatProcessor`.

## Goals / Non-Goals

**Goals:**
- Move `GraphProcessor` to `src/muggle/core/graph_processor.py`.
- Remove `ChatProcessor` implementation.
- Centralize `ProcessorInterface` for better discoverability.
- Update all references (imports, error messages) to reflect the new structure.

**Non-Goals:**
- Changing the LangGraph workflow logic itself (out of scope for this structural change).
- Adding new features to the graph.

## Decisions

### Decision: Relocate GraphProcessor to Core
- **Choice**: Move `src/muggle/experimental/graph_processor.py` to `src/muggle/core/graph_processor.py`.
- **Rationale**: The implementation is no longer experimental; it is the production processor.
- **Alternatives**: Keeping it in `experimental` (confusing for production code) or renaming it to `CoreProcessor` (unnecessary rename).

### Decision: Centralize ProcessorInterface in core/__init__.py
- **Choice**: Move the `ProcessorInterface` abstract base class from `processor.py` to `src/muggle/core/__init__.py`.
- **Rationale**: `ProcessorInterface` is a shared contract. Placing it in `__init__.py` allows clean imports like `from muggle.core import ProcessorInterface`.
- **Alternatives**: Keeping it in a separate `interface.py` (adds file bloat for a single class).

### Decision: Remove ChatProcessor and processor.py
- **Choice**: Delete `src/muggle/core/processor.py` after moving the interface.
- **Rationale**: `ChatProcessor` is legacy and its functionality is fully superseded by `GraphProcessor`. Removing it reduces maintenance overhead and confusion.
- **Alternatives**: Deprecating `ChatProcessor` (adds technical debt).

### Decision: Update Monitoring Terminology
- **Choice**: Change "ChatProcessor" to "Processor" in `src/muggle/blueprints/monitoring.py` error messages.
- **Rationale**: Decouples the monitoring logic from specific implementation class names, making it more resilient to future changes.

## Risks / Trade-offs

- **[Risk] Broken Imports** → **Mitigation**: Perform a project-wide search for `muggle.experimental.graph_processor` and `muggle.core.processor` and update to the new paths.
- **[Risk] Test Failures** → **Mitigation**: Update existing tests (e.g., `tests/test_app.py`, `tests/verify_milvus.py`) that might be importing these classes.
