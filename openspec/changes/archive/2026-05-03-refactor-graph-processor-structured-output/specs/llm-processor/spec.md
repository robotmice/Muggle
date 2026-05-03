## ADDED Requirements

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
