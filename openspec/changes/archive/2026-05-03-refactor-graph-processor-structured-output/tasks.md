## 1. Preparation

- [x] 1.1 Verify existing tests pass before refactoring (`poetry run pytest`).
- [x] 1.2 Identify all `create_agent` usage points in `src/muggle/core/graph_processor.py`.

## 2. Core Refactoring (graph_processor.py)

- [x] 2.1 Update imports: Add `SystemMessage` from `langchain_core.messages`, remove `create_agent` from `langchain.agents`.
- [x] 2.2 Refactor `intent_check_node`: Implement direct model invocation with `with_structured_output(IntentCheckResult)`.
- [x] 2.3 Refactor `query_rewrite_node`: Implement direct model invocation with `with_structured_output(QueryRewriteResult)`.
- [x] 2.4 Refactor `inquiry_node`: Implement direct model invocation with `with_structured_output(InquiryResult)`.
- [x] 2.5 Clean up node return values: Directly use the Pydantic result objects instead of `pydash.get(state, "structured_response...")`.

## 3. Test Refactoring

- [x] 3.1 Update `tests/test_llm.py`: Shift from patching `create_agent` to patching `ModelRegistry.get_model` or the LLM instance directly.
- [x] 3.2 Update `tests/test_rag.py`: Shift from patching `create_agent` to patching `ModelRegistry.get_model` or the LLM instance directly.
- [x] 3.3 Ensure all tests pass with the new structured output pattern.

## 4. Final Validation

- [x] 4.1 Run full test suite (`poetry run pytest`).
- [x] 4.2 Verify that message history (multi-turn) is correctly preserved in the graph state.
