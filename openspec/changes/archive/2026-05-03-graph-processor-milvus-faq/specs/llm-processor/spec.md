## MODIFIED Requirements

### Requirement: Graph-Based Processing Workflow
The \`GraphProcessor\` SHALL execute a multi-node LangGraph workflow to process user inquiries, incorporating a dedicated RAG pipeline.

#### Scenario: Successful inquiry processing with RAG
- **WHEN** a user sends a valid inquiry
- **THEN** the graph executes the \`intent_check\` node
- **AND** it MUST execute the \`query_rewrite\` node to optimize the search query based on conversation history
- **AND** it MUST execute the \`retrieval\` node to fetch relevant context from Milvus
- **AND** it MUST execute the \`inquiry\` node to generate a grounded response using the retrieved context
- **AND** the final response is returned to the user

### Requirement: Registry-Driven Processing
The \`GraphProcessor\` MUST utilize the \`PromptRegistry\` to retrieve system prompts for its internal graph nodes and inject retrieved context via Jinja2.

#### Scenario: Node-specific prompt injection with context
- **WHEN** the \`inquiry\` node is executed
- **THEN** it MUST retrieve its corresponding system prompt from the \`PromptRegistry\`
- **AND** it MUST inject retrieved FAQ context into the \`{{ context }}\` placeholder using Jinja2 rendering.

## ADDED Requirements

### Requirement: Context-Aware Query Rewriting
The system SHALL support rewriting user queries to be self-contained and optimized for vector search by considering the conversation history.

#### Scenario: Rewrite conversational query
- **WHEN** a user asks a follow-up question (e.g., \"Tell me more about it\")
- **THEN** the \`query_rewrite\` node MUST generate a standalone query that resolves pronouns or implicit context.
- **AND** the resulting query MUST be stored in the \`vector_store_query\` state field.

### Requirement: Isolated Retrieval Node
The system SHALL have a dedicated retrieval node that performs vector searches without invoking an LLM.

#### Scenario: Milvus search execution
- **WHEN** the \`retrieval\` node receives a \`vector_store_query\`
- **THEN** it MUST call the \`VectorStoreManager.search\` method
- **AND** it MUST store the list of resulting document entities in the \`context\` state field.
