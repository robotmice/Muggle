# Capability: chat-interface

## Purpose
TBD - Defines the frontend user interface for the chat application.

## Requirements

### Requirement: User Interface
The system SHALL provide a single-page chat interface where users can send messages and view responses. It MUST manage a `thread_id` using `sessionStorage` to maintain conversational context.

#### Scenario: User sends a message
- **WHEN** the user types a message in the input field and clicks the "Send" button
- **THEN** the message is added to the chat history and a request is sent to the backend

#### Scenario: User receives a response
- **WHEN** the backend returns a response
- **THEN** the response is displayed in the chat history

#### Scenario: User sends a message with session context
- **WHEN** the user sends a message
- **THEN** the request to the backend SHOULD include the `thread_id` if it exists in `sessionStorage`

#### Scenario: User receives a thread ID from server
- **WHEN** the backend returns a response with a `thread_id`
- **THEN** the frontend MUST save this ID in `sessionStorage` for future requests in the same tab.
