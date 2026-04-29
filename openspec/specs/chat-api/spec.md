# Capability: chat-api

## Purpose
TBD - Defines the backend API for handling chat messages.

## Requirements

### Requirement: Chat Endpoint
The backend SHALL expose a POST endpoint at `/chat` that accepts a JSON payload containing the user's message. This endpoint MUST be defined within a dedicated `chat` blueprint.

#### Scenario: Successful message processing
- **WHEN** a valid POST request is received at `/chat` with a JSON payload `{ "message": "hello" }`
- **THEN** the system returns a 200 OK status and a JSON response `{ "response": "..." }`

### Requirement: Error Handling
The backend SHALL return a 400 Bad Request if the payload is malformed.

#### Scenario: Missing message field
- **WHEN** a POST request is received at `/chat` without a "message" field
- **THEN** the system returns a 400 Bad Request
