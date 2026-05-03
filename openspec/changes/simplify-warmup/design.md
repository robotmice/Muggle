## Context

The current implementation of `warm_up` in `src/muggle/core/graph_processor.py` manually checks if a model is registered before attempting to load it. This check is duplicated logic from the `ModelRegistry` class.

## Goals / Non-Goals

**Goals:**
- Simplify the `warm_up` method implementation.
- Ensure consistent error reporting for missing models.

**Non-Goals:**
- Change the lazy-loading logic of the registry.
- Change the public API of `ChatProcessor` or `ModelRegistry`.

## Decisions

### Delegate validation to ModelRegistry
- **Choice**: Remove `self.registry.is_registered` check from `warm_up`.
- **Rationale**: `ModelRegistry.get_model()` already performs this check and raises a `ValueError`. Duplicating this check in `ChatProcessor` adds noise and maintenance overhead.
- **Alternatives**: Keeping the check provides more specific error messages in `ChatProcessor`, but the current messages are almost identical to what the registry provides.

## Risks / Trade-offs

- **Risk**: Registry's error message might slightly differ from the current custom message.
- **Mitigation**: The registry error ("Model alias '...' is not registered.") is sufficiently clear and compatible with existing expectations.