## MODIFIED Requirements

### Requirement: User Interface
The system SHALL provide a single-page chat interface where users can send messages and view responses. It MUST manage a `thread_id` using `sessionStorage` to maintain conversational context.

#### Scenario: User sends a message with session context
- **WHEN** the user sends a message
- **THEN** the request to the backend SHOULD include the `thread_id` if it exists in `sessionStorage`

#### Scenario: User receives a thread ID from server
- **WHEN** the backend returns a response with a `thread_id`
- **THEN** the frontend MUST save this ID in `sessionStorage` for future requests in the same tab.
