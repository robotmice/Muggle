## Context

The current codebase has three intertwined inconsistencies:

1. **Hardcoded retry limit**: `validation_router` in `state.py` checks `state.retry_count >= 5`. The `threshold` already flows from config.toml → `get_validate_params()` → `ValidateNode`, but `max_retries` does not follow the same path.

2. **Imprecise field name**: `retry_count` counts all attempts (including the first), not just retries. `attempt_count` is more accurate.

3. **Mixed naming conventions**: Node/prompt identifiers mix verbs (`summarize`, `validate`, `query-rewrite`), nouns (`retrieval`, `inquiry`), and adjectives (`unhandled`). The project convention should use nouns consistently.

All three changes cascade through the same set of files, so bundling them avoids multiple rounds of renames.

## Goals / Non-Goals

**Goals:**
- `attempt_count` replaces `retry_count` in all production and test code
- `max_attempts` is configurable in config.toml under `[validate]`, with a default of 5
- Node/prompt naming uses nouns consistently: `summarization`, `validation`, `fallback`
- `ValidationRouter` class replaces the `validation_router` function, receiving `max_attempts` at construction

**Non-Goals:**
- No changes to LangGraph routing behavior or pipeline logic
- No changes to retry counter reset logic (IntentCheck still resets to 0)
- No changes to `query-rewrite`, `retrieval`, `inquiry`, `intent-check` (already nouns)
- No changes to external dependency `SummarizationNode` (from langmem)

## Decisions

### Decision 1: `ValidationRouter` as a callable class

Putting `max_attempts` on `WorkflowState` mixes config with conversation state. A callable class holds the config value naturally:

```python
class ValidationRouter:
    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts

    def __call__(self, state: WorkflowState) -> str:
        if state.pass_validation:
            return END
        if state.attempt_count >= self.max_attempts:
            return STR_NODE_FALLBACK
        return STR_NODE_SUMMARIZATION
```

**Alternatives considered:**
- Adding `max_attempts` to `WorkflowState`: Works but pollutes conversation state with a fixed config value. Rejected.
- Module-level global: Works but makes testing harder. Rejected.

### Decision 2: Single-pass rename, no backwards compatibility shims

All renames happen atomically — old names are removed, not deprecated. No `_old_name = NewName` aliases. The change touches ~15 files but each rename is mechanical.

### Decision 3: `fallback` over `rejection`

The node handles out-of-scope queries with a polite decline. "Fallback" describes what it IS (a fallback path), while "rejection" describes what it DOES. Nouns describe identity, so `fallback` is the better noun.

## Risks / Trade-offs

- **Breaking import paths**: External consumers of `muggle.core.guard.unhandled` or `muggle.core.validate` will break. This is a private package, no known external consumers. Mitigation: commit message clearly states the rename.
- **Missed references**: String-based references (prompt names in `.md` frontmatter) could be missed by grep. Mitigation: search for both old and new strings after rename, run full test suite.
