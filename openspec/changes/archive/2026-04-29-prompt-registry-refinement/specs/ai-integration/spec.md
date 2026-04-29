## ADDED Requirements

### Requirement: Registry-Driven Chat Processing
The `ChatProcessor` MUST utilize the `PromptRegistry` to retrieve and apply templates before invoking the AI model.

#### Scenario: Default system prompt injection
- **WHEN** `get_response("Hello")` is called
- **THEN** the processor MUST retrieve the "default" system prompt from the `PromptRegistry` and include it in the message list sent to the LLM.

### Requirement: Fail-Safe for Missing Prompts
The `ChatProcessor` MUST gracefully handle cases where a required prompt is missing from the registry.

#### Scenario: Missing system prompt
- **WHEN** a required system prompt is missing and `PromptNotFoundError` is raised
- **THEN** the processor MUST log the error and return a user-friendly error message indicating that the AI configuration is incomplete.
