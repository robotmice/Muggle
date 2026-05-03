## Context

`GraphProcessor` currently utilizes LangGraph for intent checking and inquiry handling. A critical bug exists where the conversation history is lost between turns. This happens because the `WorkflowState` Pydantic model defines the `Field(default_factory=list)` inside the `Annotated` block, causing LangGraph to ignore the `add_messages` reducer. Consequently, the message list is overwritten instead of appended. Additionally, the `/chat` API does not pass a `thread_id` to the processor, which would lead to shared state across all users once the reducer issue is fixed.

## Goals / Non-Goals

**Goals:**
- Fix the `WorkflowState` definition so `add_messages` works correctly.
- Ensure the `/chat` endpoint accepts and forwards a `thread_id` to isolate user sessions.
- Provide automated tests verifying multi-turn conversational memory.

**Non-Goals:**
- Implement persistent memory (e.g., SQLiteSaver or PostgresSaver). `InMemorySaver` is sufficient for current local scope, provided the session isolation (`thread_id`) works.

## Decisions

- **Decision 1: Pydantic Annotation Order**: Move the `Field` definition outside the `Annotated` block in `WorkflowState`.
  - *Rationale*: This is required by LangGraph/Pydantic for the reducer to be recognized.
- **Decision 2: Server-Managed `thread_id`**: The `/chat` payload will accept an optional `thread_id`. 
  - If provided: The server uses it to retrieve existing state.
  - If missing: The server generates a unique UUID (v4) and uses it as the new `thread_id`.
  - The server MUST return the `thread_id` used in the JSON response (e.g., `{"response": "...", "thread_id": "..."}`).
  - *Rationale*: This enables the browser to manage sessions via `sessionStorage` without requiring the client to handle UUID generation logic initially.
- **Decision 3: Frontend Persistence**: The frontend will use `sessionStorage.getItem('muggle_thread_id')` to retrieve the current thread ID and `sessionStorage.setItem('muggle_thread_id', ...)` to save the one returned by the server.
  - *Rationale*: `sessionStorage` is appropriate as it persists for the duration of the page session (tab), matching the requirement for multi-turn conversations within a single session.

## Risks / Trade-offs

- [Risk] Memory leaks with `InMemorySaver`. → Mitigation: Since this is currently an experimental/local project, `InMemorySaver` is acceptable. Future scaling will require a persistent checkpointer, which is a separate architectural concern.
