## ADDED Requirements

### Requirement: Conversational Memory
The `GraphProcessor` SHALL maintain the history of the conversation across multiple turns for a given `thread_id`.

#### Scenario: Multi-turn recall
- **WHEN** a user sends multiple messages within the same `thread_id` (e.g., "Hi, I'm Bob" followed by "What is my name?")
- **THEN** the LLM successfully recalls information from the previous messages (e.g., responds "Bob").
