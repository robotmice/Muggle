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
The `GraphProcessor` SHALL execute a multi-node LangGraph workflow to process user inquiries, incorporating a dedicated RAG pipeline.

#### Scenario: Successful inquiry processing
- **WHEN** a user sends a valid inquiry
- **THEN** the graph executes the `intent_check` node, followed by the `inquiry` node
- **AND** the final response is returned to the user

#### Scenario: Successful inquiry processing with RAG
- **WHEN** a user sends a valid inquiry
- **THEN** the graph executes the `intent_check` node
- **AND** it MUST execute the `query_rewrite` node to optimize the search query based on conversation history
- **AND** it MUST execute the `retrieval` node to fetch relevant context from Milvus
- **AND** it MUST execute the `inquiry` node to generate a grounded response using the retrieved context
- **AND** the final response is returned to the user

### Requirement: Handling Unhandled Intents
The `GraphProcessor` SHALL gracefully handle messages that do not pass the intent verification step.

#### Scenario: Invalid intent detected
- **WHEN** the `intent_check` node determines the message is out of scope or invalid
- **THEN** the graph routes to the `unhandled` node
- **AND** a standard rejection message ("I cannot respond to this question.") is returned

### Requirement: Registry-Driven Processing
The `GraphProcessor` MUST utilize the `PromptRegistry` to retrieve system prompts for its internal graph nodes and inject retrieved context via Jinja2.

#### Scenario: Node-specific prompt injection
- **WHEN** a graph node (like `intent_check`) is executed
- **THEN** it MUST retrieve its corresponding system prompt from the `PromptRegistry` using the configured constants.

#### Scenario: Node-specific prompt injection with context
- **WHEN** the `inquiry` node is executed
- **THEN** it MUST retrieve its corresponding system prompt from the `PromptRegistry`
- **AND** it MUST inject retrieved FAQ context into the `{{ context }}` placeholder using Jinja2 rendering.

### Requirement: Context-Aware Query Rewriting
The system SHALL support rewriting user queries to be self-contained and optimized for vector search by considering the conversation history.

#### Scenario: Rewrite conversational query
- **WHEN** a user asks a follow-up question (e.g., "Tell me more about it")
- **THEN** the `query_rewrite` node MUST generate a standalone query that resolves pronouns or implicit context.
- **AND** the resulting query MUST be stored in the `vector_store_query` state field.

### Requirement: Isolated Retrieval Node
The system SHALL have a dedicated retrieval node that performs vector searches without invoking an LLM.

#### Scenario: Milvus search execution
- **WHEN** the `retrieval` node receives a `vector_store_query`
- **THEN** it MUST call the `VectorStoreManager.search` method
- **AND** it MUST store the list of resulting document entities in the `context` state field.

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

### Requirement: Robust Processor Initialization
The `GraphProcessor` SHALL validate its configuration during initialization (warmup) to ensure all required components (like models) are correctly defined.

#### Scenario: Validation of missing models during warmup
- **WHEN** the processor is warmed up with a missing model
- **THEN** it SHALL still raise a ValueError (delegated to the registry).

### Requirement: Structured Node Execution
The `GraphProcessor` nodes (Intent Check, Query Rewrite, Inquiry) SHALL utilize the LLM's structured output capability instead of agent-based executors to ensure predictable, schema-validated results and eliminate agent-loop overhead.

#### Scenario: Intent check with structured output
- **WHEN** the `intent_check` node executes
- **THEN** it MUST invoke the LLM with the `IntentCheckResult` schema using the `with_structured_output` method
- **AND** it MUST explicitly prepare the message list containing the retrieved system prompt and the current conversation history.

#### Scenario: Query rewrite with structured output
- **WHEN** the `query_rewrite` node executes
- **THEN** it MUST invoke the LLM with the `QueryRewriteResult` schema using the `with_structured_output` method
- **AND** it MUST explicitly prepare the message list containing the retrieved system prompt and the current conversation history.

#### Scenario: Inquiry generation with structured output
- **WHEN** the `inquiry` node executes
- **THEN** it MUST invoke the LLM with the `InquiryResult` schema using the `with_structured_output` method
- **AND** it MUST explicitly prepare the message list containing the retrieved system prompt and the current conversation history.
