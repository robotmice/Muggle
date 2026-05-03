# Capability: llm-processor

## Purpose
TBD - Defines the logic for processing messages using LLM models and workflows.

## Requirements

### Requirement: Modular Processor Interface
The system SHALL define a clear interface for processing messages, with `GraphProcessor` as the primary implementation.

#### Scenario: Standard graph-based processing
- **WHEN** the processor receives a message
- **THEN** it executes the compiled LangGraph workflow to generate a response

### Requirement: Graph-Based Processing Workflow
The `GraphProcessor` SHALL execute a multi-node LangGraph workflow to process user inquiries, including an explicit intent verification step.

#### Scenario: Successful inquiry processing
- **WHEN** a user sends a valid inquiry
- **THEN** the graph executes the `intent_check` node, followed by the `inquiry` node
- **AND** the final response is returned to the user

### Requirement: Handling Unhandled Intents
The `GraphProcessor` SHALL gracefully handle messages that do not pass the intent verification step.

#### Scenario: Invalid intent detected
- **WHEN** the `intent_check` node determines the message is out of scope or invalid
- **THEN** the graph routes to the `unhandled` node
- **AND** a standard rejection message ("I cannot respond to this question.") is returned

### Requirement: Registry-Driven Processing
The `GraphProcessor` MUST utilize the `PromptRegistry` to retrieve system prompts for its internal graph nodes (e.g., intent check, inquiry handler).

#### Scenario: Node-specific prompt injection
- **WHEN** a graph node (like `intent_check`) is executed
- **THEN** it MUST retrieve its corresponding system prompt from the `PromptRegistry` using the configured constants.

### Requirement: Fail-Safe for Missing Prompts in Nodes
The `GraphProcessor` MUST gracefully handle cases where a required prompt for a graph node is missing from the registry.

#### Scenario: Missing node prompt
- **WHEN** a required system prompt for a node is missing during execution
- **THEN** the processor MUST log the error and return a user-friendly error message indicating that the configuration is incomplete.

### Requirement: Conversational Memory
The `GraphProcessor` SHALL maintain the history of the conversation across multiple turns for a given `thread_id`.

#### Scenario: Multi-turn recall
- **WHEN** a user sends multiple messages within the same `thread_id` (e.g., "Hi, I'm Bob" followed by "What is my name?")
- **THEN** the LLM successfully recalls information from the previous messages (e.g., responds "Bob").
