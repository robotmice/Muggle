# Capability: chat-api

## Purpose
TBD - Defines the backend API for handling chat messages.

## Requirements

### Requirement: Chat Endpoint
The backend SHALL expose a POST endpoint at `/chat` that accepts a JSON payload containing the user's message. It MUST also accept an optional `thread_id` string to isolate conversational sessions. If no `thread_id` is provided, the server MUST generate a new unique identifier. The response MUST include the `thread_id` used for the request. This endpoint MUST be defined within a dedicated `chat` blueprint.

#### Scenario: Successful message processing with new thread
- **WHEN** a valid POST request is received at `/chat` with a JSON payload `{ "message": "hello" }` (no thread_id)
- **THEN** the system returns a 200 OK status and a JSON response `{ "response": "...", "thread_id": "<new-uuid>" }`

#### Scenario: Threaded message processing with existing thread
- **WHEN** a valid POST request is received at `/chat` with a JSON payload `{ "message": "hello", "thread_id": "user-123" }`
- **THEN** the system returns a 200 OK status and a JSON response `{ "response": "...", "thread_id": "user-123" }`, and processes the message within the context of `user-123`.

### Requirement: Error Handling
The backend SHALL return a 400 Bad Request if the payload is malformed.

#### Scenario: Missing message field
- **WHEN** a POST request is received at `/chat` without a "message" field
- **THEN** the system returns a 400 Bad Request

### Requirement: Frontend Integration
The frontend SHALL use `llm` class names for message styling and internal identifiers.

#### Scenario: LLM message display
- **WHEN** a message is received from the backend
- **THEN** it MUST be appended with the `llm` type and styled accordingly.
