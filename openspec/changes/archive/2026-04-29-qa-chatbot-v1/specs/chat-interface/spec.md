## ADDED Requirements

### Requirement: User Interface
The system SHALL provide a single-page chat interface where users can send messages and view responses.

#### Scenario: User sends a message
- **WHEN** the user types a message in the input field and clicks the "Send" button
- **THEN** the message is added to the chat history and a request is sent to the backend

#### Scenario: User receives a response
- **WHEN** the backend returns a response
- **THEN** the response is displayed in the chat history
