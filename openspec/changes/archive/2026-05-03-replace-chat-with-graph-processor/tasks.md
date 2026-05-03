## 1. Preparation and Interface Relocation

- [x] 1.1 Move `ProcessorInterface` abstract base class to `src/muggle/core/__init__.py`.
- [x] 1.2 Update `src/muggle/core/processor.py` to import `ProcessorInterface` from the new location.

## 2. Relocate GraphProcessor

- [x] 2.1 Move `src/muggle/experimental/graph_processor.py` to `src/muggle/core/graph_processor.py`.
- [x] 2.2 Update imports in `src/muggle/core/graph_processor.py` to reference `ProcessorInterface` from `muggle.core`.
- [x] 2.3 Update `src/muggle/app.py` to import `GraphProcessor` from its new location in `muggle.core.graph_processor`.

## 3. Remove Legacy Implementation

- [x] 3.1 Delete `src/muggle/core/processor.py` (which contains `ChatProcessor`).
- [x] 3.2 Perform a global search for `ChatProcessor` and replace any remaining references with `GraphProcessor` or `Processor` where appropriate.

## 4. Refine Monitoring and Error Handling

- [x] 4.1 Update `src/muggle/blueprints/monitoring.py` error messages to refer to "Processor" instead of "ChatProcessor".
- [x] 4.2 Ensure the logger in `src/muggle/app.py` refers to the correct processor in its error messages.

## 5. Verification and Cleanup

- [x] 5.1 Search and update all test files that import from `muggle.experimental` or `muggle.core.processor`.
- [x] 5.2 Run `pytest` to verify the application still functions correctly after refactoring.
- [x] 5.3 Verify the health check endpoint `/health` reflects the new terminology.

## 6. Specification Synchronization

- [x] 6.1 Run `/opsx:sync` (or `openspec sync`) to update the main `llm-processor` specification with the changes from the delta spec.
