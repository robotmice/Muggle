## Why

The current implementation of `GraphProcessor` relies on a `create_agent` wrapper which internally uses LangChain's `AgentExecutor`. This introduces unnecessary complexity, agent-loop overhead, and a risk of implicit tool-calling hallucinations or "thinking" tokens. Moving to raw LLM calls with `with_structured_output` provides a more direct, predictable, and performant way to handle structured node logic while explicitly managing conversation history.

## What Changes

- **Node Refactoring**: Replace `create_agent` calls in `intent_check_node`, `query_rewrite_node`, and `inquiry_node` with direct LLM calls using `with_structured_output`.
- **Structured Outputs**: Utilize Pydantic models (`IntentCheckResult`, `QueryRewriteResult`, `InquiryResult`) directly with the LLM's structured output capability.
- **Message Management**: Explicitly prepare message lists (system prompt + history) for each LLM call within the nodes.
- **Dependency Removal**: Remove the `langchain.agents.create_agent` import and its usage.
- **Test Updates**: Refactor unit tests that currently mock `create_agent` to mock the underlying LLM instance's `invoke` or `with_structured_output` methods.

## Capabilities

### New Capabilities
- None (refactor of existing implementation).

### Modified Capabilities
- `llm-processor`: Standardize on structured output calls and explicit message preparation within graph nodes.

## Impact

- `src/muggle/core/graph_processor.py`: Significant logic changes within node functions.
- `tests/test_llm.py`: Mocking strategy change.
- `tests/test_rag.py`: Mocking strategy change.
- System performance: Reduced latency by eliminating agent-loop overhead.
- Reliability: Improved predictability of node outputs.
