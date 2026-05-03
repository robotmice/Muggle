## Why

The InquiryNode occasionally produces responses that fail basic quality standards — empty responses, hallucinated coverage details, or compliance-violating language. Adding a validation gate with automatic retry catches these failures before they reach the user, without requiring manual intervention.

## What Changes

- Add a `ValidateNode` that scores Inquiry output via LLM structured output against the existing `prompt-validate.md` quality prompt
- Add `retry_count` and `pass_validation` fields to `WorkflowState`
- Insert ValidateNode after InquiryNode in the graph, with conditional routing: pass → END, fail with retries remaining → loop back to Summarization, fail with exhausted retries → UnhandledNode
- Add a `validation_router` function alongside the existing `ingest_router`
- Add `[validate]` section to `config.toml` with a `threshold` parameter (default 0.8)
- Reset `retry_count` to 0 in IntentCheckNode so each new user message starts with a clean counter

## Capabilities

### New Capabilities

- `response-validation`: LLM-based quality gate that scores InquiryNode output, loops back for blind re-generation on failure (up to 5 attempts), and routes to UnhandledNode when retries are exhausted

### Modified Capabilities

None — existing specs unchanged.

## Impact

- **Affected files**: `graph_processor.py`, `state.py`, `guard/intent_check.py`, `config.toml`
- **New files**: `core/validate.py` (ValidateNode + ValidationResult model)
- **Constants already exist**: `STR_NODE_VALIDATE`, `STR_PROMPT_VALIDATE` in `shared/constants.py`
- **Prompt already exists**: `infra/prompts/system/prompt-validate.md`
- **Additional LLM call per response**: minimum 1 (validation), maximum 5 (all retries fail)
