## Why

The codebase has two inconsistencies that create friction: the hardcoded `retry_count >= 5` threshold in `validation_router` prevents tuning retry behavior without a code change, and the node/prompt naming mixes verbs (`summarize`, `validate`), nouns (`retrieval`, `inquiry`), and adjectives (`unhandled`) making the convention unclear to newcomers.

## What Changes

- Rename `retry_count` to `attempt_count` across WorkflowState, nodes, and tests — "attempt" counts what happened, "retry" implies only repeats
- Make `max_attempts` configurable via `[validate]` section in `config.toml` instead of hardcoding `5`
- Convert `validation_router` from a plain function to a `ValidationRouter` class that receives `max_attempts` at construction
- **BREAKING**: Rename `STR_NODE_SUMMARIZE` → `STR_NODE_SUMMARIZATION`, `STR_NODE_VALIDATE` → `STR_NODE_VALIDATION`, `STR_NODE_UNHANDLED` → `STR_NODE_FALLBACK` (and corresponding prompt constants)
- **BREAKING**: Rename `UnhandledNode` → `FallbackNode`, `ValidateNode` → `ValidationNode`
- **BREAKING**: Rename `unhandled.py` → `fallback.py`, `validate.py` → `validation.py`
- **BREAKING**: Rename prompt template `prompt-validate.md` → `prompt-validation.md`
- Keep existing names for `query-rewrite`, `retrieval`, `inquiry`, `intent-check` (already nouns)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `response-validation`: `retry_count` renamed to `attempt_count`; max attempts is now configurable via `max_attempts` in config.toml rather than hardcoded to 5
- `graph-node-architecture`: Node naming convention standardized to nouns; `ValidationNode` and `FallbackNode` replace `ValidateNode` and `UnhandledNode`

## Impact

- All files importing from `muggle.core.state`, `muggle.core.validate`, `muggle.core.guard.unhandled`
- `config.toml` and `config.py` (`get_validate_params`)
- Prompt template file: `prompt-validate.md` renamed
- Tests: `test_validate.py`
- `openspec/specs/response-validation/spec.md` and `openspec/specs/graph-node-architecture/spec.md` need delta updates
