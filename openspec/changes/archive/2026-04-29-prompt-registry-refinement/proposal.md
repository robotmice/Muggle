## Why

As the project grows, the unified `registry.py` is becoming a "kitchen sink" for different types of registries. We need to modularize the registry system and introduce domain-specific exceptions to improve maintainability, testability, and error handling.

## What Changes

- **Registry Modularization**: Split `muggle/registry.py` into separate modules for Model and Prompt registries.
- **Custom Exceptions**: Introduce a dedicated `exceptions.py` module to house domain-specific errors like `PromptNotFoundError`.
- **Improved Error Feedback**: Update the `PromptRegistry` and `ChatProcessor` to provide more granular error information using these new exceptions.

## Capabilities

### New Capabilities
- `error-handling`: Definition and usage of domain-specific exceptions across the AI pipeline.

### Modified Capabilities
- `prompt-registry`: Update the registry implementation to use custom exceptions and a modular file structure.

## Impact

- `muggle/registry/`: New directory to house modularized registries.
- `muggle/exceptions.py`: New module for custom exceptions.
- `muggle/ai.py`: Updated imports and error handling logic.
- `muggle/app.py`: Updated imports for registry initialization.
