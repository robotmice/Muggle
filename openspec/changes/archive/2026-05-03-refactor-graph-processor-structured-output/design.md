## Context

The `GraphProcessor` implementation currently uses a `create_agent` function to execute logic within each node. This function likely wraps LangChain's `AgentExecutor`, which is designed for autonomous tool-use. In our case, the nodes are deterministic and only require structured output from the LLM based on a schema. Using an agent executor introduces latency, complexity, and the potential for "implicit tool call" hallucinations where the model attempts to use tools even when none are provided.

## Goals / Non-Goals

**Goals:**
- Eliminate `AgentExecutor` overhead in `GraphProcessor` nodes.
- Use LangChain's `with_structured_output` for type-safe, validated LLM responses.
- Explicitly manage the flow of messages (System + User + History) within each node.
- Maintain full compatibility with existing `WorkflowState` and graph edges.

**Non-Goals:**
- Changing the LangGraph topology (nodes, edges, and conditional logic remain unchanged).
- Modifying the existing Pydantic schemas (`IntentCheckResult`, `QueryRewriteResult`, `InquiryResult`).
- Changing how models or prompts are registered or retrieved.

## Decisions

### 1. Shift to `with_structured_output`
Instead of using `create_agent`, each node will retrieve the model instance from the registry and apply `.with_structured_output(Schema)`.
- **Rationale**: This is the standard LangChain way to enforce structured responses without the overhead of an agent loop. It works natively with Pydantic and supports both tool-calling and JSON-mode backends automatically.

### 2. Explicit Message Preparation
Each node will be responsible for constructing the list of messages sent to the LLM.
- **Implementation**:
  ```python
  messages = [SystemMessage(content=system_prompt)] + state.messages
  result = model.with_structured_output(Schema).invoke(messages)
  ```
- **Rationale**: Since `WorkflowState` uses `Annotated[list, add_messages]`, `state.messages` already contains the full conversation history. Prepending the system prompt ensures the LLM has context and instructions for the current turn.

### 3. Unified Error Handling
Nodes will handle potential parsing errors or LLM failures consistently, potentially falling back to safe defaults if the structured output fails.

### 4. Test Refactoring
Unit tests in `tests/test_llm.py` and `tests/test_rag.py` will be updated to mock the model instance returned by `registry.get_model()`.
- **Strategy**: Patch `ModelRegistry.get_model` to return a mock LLM. The mock LLM's `with_structured_output` will return another mock (the "structured model") whose `invoke` returns the desired Pydantic object.

## Risks / Trade-offs

- **[Risk] Model Compatibility** → **Mitigation**: `with_structured_output` is broadly supported by the providers we use (DeepSeek, DashScope). We will verify compatibility during implementation.
- **[Risk] History Bloat** → **Mitigation**: While we are passing the full history, this was already happening inside `AgentExecutor`. We maintain parity but with more visibility.
