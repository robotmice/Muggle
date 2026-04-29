## Context

The initial implementation of the `PromptRegistry` was added directly to `muggle/registry.py`. While sufficient for a prototype, this structure leads to bloated modules. Additionally, the system relies on generic Python exceptions (like `FileNotFoundError`), which don't provide domain-specific context for AI operations.

## Goals / Non-Goals

**Goals:**
- Move `ModelRegistry` and `PromptRegistry` into a `muggle/registry/` package.
- Create a `muggle/exceptions.py` file for custom AI exceptions.
- Implement `PromptNotFoundError` and ensure it's raised by `PromptRegistry`.
- **Integrate `PromptRegistry` into `ChatProcessor` to enable template-driven responses.**
- Update all imports in `ai.py`, `app.py`, and `tests/` to use the new structure.

**Non-Goals:**
- Adding a base `Registry` class for inheritance (unless strictly necessary).
- Refactoring `ConfigManager` or other unrelated modules.

## Decisions

### 1. Module Structure: Package-based Registries
- **Rationale**: Converting `registry.py` into a package (`muggle/registry/`) with `__init__.py`, `model.py`, and `prompt.py` allows for better organization as new registry types (e.g., ToolRegistry) are added.
- **Alternatives**: Keeping them in one file (leads to bloat); separate top-level files like `model_registry.py` (less organized than a package).

### 2. Centralized Exceptions Module
- **Rationale**: A dedicated `muggle/exceptions.py` provides a single source of truth for all domain-specific errors, making it easier for developers to know what to catch.
- **Alternatives**: Defining exceptions inside the registry modules (leads to circular imports if multiple modules need them).

### 3. Exception Hierarchy
- **Rationale**: `PromptNotFoundError` will inherit from a base `MuggleError` to allow for catching all project-specific errors at once if desired.

## Risks / Trade-offs

- **[Risk] Broken Imports** → **Mitigation**: Perform a global search for registry imports and update them. Ensure all tests pass after refactoring.
- **[Risk] Circular Dependencies** → **Mitigation**: Keep the `exceptions.py` module leaf-level (no internal imports from other muggle modules).
Trade-offs

- **[Risk] Broken Imports** → **Mitigation**: Perform a global search for registry imports and update them. Ensure all tests pass after refactoring.
- **[Risk] Circular Dependencies** → **Mitigation**: Keep the `exceptions.py` module leaf-level (no internal imports from other muggle modules).
