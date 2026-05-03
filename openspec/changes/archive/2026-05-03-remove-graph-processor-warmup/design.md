## Context

`GraphProcessor` currently has a graceful-startup pattern: `warm_up()` validates the LLM is reachable, `is_initialized()` and `last_error` expose the result, and `/health` reports it. The warm-up failure is caught and logged in `app.py` — the server starts regardless. This adds six members to the processor class for a guard that doesn't prevent anything.

## Goals / Non-Goals

**Goals:**
- Remove `warm_up()`, `is_initialized()`, `last_error`, `_ready`, and `_last_error` from `GraphProcessor`
- Remove the `try/except` warm-up block from `app.py`
- Simplify `/health` to a single existence check on the processor
- Remove `warm_up()` calls from tests

**Non-Goals:**
- Changing the `/chat` endpoint behavior
- Changing the `ProcessorInterface` ABC
- Adding any new health-check mechanism

## Decisions

### Drop warm-up entirely rather than inline it

`warm_up()` currently does `self.registry.get_model(self.default_model)` — a one-liner that just verifies the model can be instantiated. The constructor already calls `registry.get_model(default_model)` on line 38, so warm-up is redundant with construction. Removing it is safe.

### Simplify /health to processor existence check

Previously `/health` checked `is_initialized()` and reported `last_error`. Since `is_initialized()` tracked only warm-up success and warm-up succeeded whenever the constructor succeeded, the check was equivalent to "does the processor exist on the app context." The simplification preserves the semantic while removing the indirection.

### No replacement health mechanism

The LLM is a runtime dependency. If it's unreachable, the `/chat` endpoint returns an error message. Adding a separate health probe for LLM connectivity would be a new feature, not part of this removal.

## Risks / Trade-offs

- **LLM unreachable at startup** → No longer caught eagerly. First `/chat` request surfaces it. Mitigation: the error message in `get_response()` already handles this case (`"Error connecting to LLM: ..."`). This is low risk since the previous warm-up didn't prevent serving traffic either.
