## Why

`GraphProcessor` currently loses conversation history in multi-turn dialogues. This is caused by a bug in the `WorkflowState` Pydantic model that prevents LangGraph's `add_messages` reducer from working correctly, resulting in the state being overwritten instead of appended. Additionally, the `/chat` API does not pass a `thread_id`, meaning all requests are processed under a default session, which would lead to shared state across users once the reducer is fixed.

## What Changes

- Correct the `WorkflowState` definition in `GraphProcessor` to ensure the `add_messages` reducer properly appends message history.
- Update the `/chat` API endpoint to accept an optional `thread_id`. If missing, the server SHALL generate a new UUID and return it in the response to allow the browser to store it in session storage.
- Update `GraphProcessor` to properly handle and route the `thread_id` to isolate user sessions.
- Update the frontend (`src/muggle/static/index.html`) to manage the `thread_id` in `sessionStorage`.
- Add multi-turn memory verification to the LLM tests.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `llm-processor`: Ensure the processor correctly maintains conversational state across multiple turns for a given thread.
- `chat-api`: The `/chat` endpoint must accept a `thread_id` parameter to isolate conversation state and return it if generated.
- `chat-interface`: The frontend must store and send the `thread_id` using `sessionStorage`.

## Impact

- **State Management**: `src/muggle/experimental/graph_processor.py`
- **API Layer**: `src/muggle/blueprints/chat.py`
- **Testing**: `tests/test_llm.py`
