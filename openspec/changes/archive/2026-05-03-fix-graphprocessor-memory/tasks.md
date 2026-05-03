## 1. GraphProcessor State Fix

- [x] 1.1 Update `WorkflowState` in `src/muggle/experimental/graph_processor.py` to move `Field(default_factory=list)` outside the `Annotated` block.
- [x] 1.2 Verify that `GraphProcessor` successfully passes local multi-turn simulation using the updated state logic.

## 2. API and Interface Updates

- [x] 2.1 Update `get_response` method signature in `ProcessorInterface` (`src/muggle/core/processor.py`) to accept an optional `thread_id`.
- [x] 2.2 Update `ChatProcessor` (`src/muggle/core/processor.py`) to accept the `thread_id` parameter to satisfy the interface requirements.
- [x] 2.3 Update the `/chat` route in `src/muggle/blueprints/chat.py` to extract an optional `thread_id`. If missing, generate a new UUID. Pass the `thread_id` to `processor.get_response()` and include it in the JSON response.

## 3. Frontend Implementation

- [x] 3.1 Update `src/muggle/static/index.html` to retrieve `muggle_thread_id` from `sessionStorage` and include it in the `/chat` request.
- [x] 3.2 Update `src/muggle/static/index.html` to save the `thread_id` returned from the server into `sessionStorage`.

## 4. Automated Testing

- [x] 3.1 Add a multi-turn conversation test in `tests/test_llm.py` for `GraphProcessor` to assert memory is preserved across multiple interactions with the same `thread_id`.
