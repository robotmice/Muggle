# Capability: llm-processor

## Purpose
TBD - Defines the logic for processing messages using LLM models and workflows.

## Requirements

### Requirement: Modular Processor Interface
The system SHALL define a clear interface for processing messages that can accommodate both simple LLM calls and LangGraph workflows.

#### Scenario: Simple LLM processing
- **WHEN** the processor receives a message
- **THEN** it uses LangChain's `init_chat_model` (initialized via the configuration utility) to generate a response

#### Scenario: Extensibility for LangGraph
- **WHEN** a LangGraph workflow is implemented in the future
- **THEN** it can replace the simple LLM wrapper without changing the `process_message` interface signature

### Requirement: Registry-Driven Chat Processing
The `ChatProcessor` MUST utilize the `PromptRegistry` to retrieve and apply templates before invoking the LLM model.

#### Scenario: Default system prompt injection
- **WHEN** `get_response("Hello")` is called
- **THEN** the processor MUST retrieve the "default" system prompt from the `PromptRegistry` and include it in the message list sent to the LLM.

### Requirement: Fail-Safe for Missing Prompts
The `ChatProcessor` MUST gracefully handle cases where a required prompt is missing from the registry.

#### Scenario: Missing system prompt
- **WHEN** a required system prompt is missing and `PromptNotFoundError` is raised
- **THEN** the processor MUST log the error and return a user-friendly error message indicating that the LLM configuration is incomplete.
