## ADDED Requirements

### Requirement: Frontend Integration
The frontend SHALL use `llm` class names for message styling and internal identifiers.

#### Scenario: LLM message display
- **WHEN** a message is received from the backend
- **THEN** it MUST be appended with the `llm` type and styled accordingly.
