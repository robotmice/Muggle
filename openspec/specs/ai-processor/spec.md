# Capability: ai-processor

## Purpose
TBD - Defines the logic for processing messages using AI models and workflows.

## Requirements

### Requirement: Modular Processor Interface
The system SHALL define a clear interface for processing messages that can accommodate both simple LLM calls and LangGraph workflows.

#### Scenario: Simple LLM processing
- **WHEN** the processor receives a message
- **THEN** it uses LangChain's `init_chat_model` (initialized via the configuration utility) to generate a response

#### Scenario: Extensibility for LangGraph
- **WHEN** a LangGraph workflow is implemented in the future
- **THEN** it can replace the simple LLM wrapper without changing the `process_message` interface signature
