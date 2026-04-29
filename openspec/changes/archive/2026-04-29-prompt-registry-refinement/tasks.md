## 1. Structural Changes

- [x] 1.1 Create `muggle/registry/` package directory with `__init__.py`
- [x] 1.2 Create `muggle/exceptions.py` with `MuggleError` and `PromptNotFoundError`
- [x] 1.3 Move `ModelRegistry` from `muggle/registry.py` to `muggle/registry/model.py`
- [x] 1.4 Move `PromptRegistry` from `muggle/registry.py` to `muggle/registry/prompt.py`
- [x] 1.5 Update `muggle/registry/__init__.py` to export both registries
- [x] 1.6 Remove the old `muggle/registry.py` file

## 2. Implementation Refinement

- [x] 2.1 Update `PromptRegistry` to raise `PromptNotFoundError` instead of `FileNotFoundError`
- [x] 2.2 Update `ChatProcessor` in `muggle/ai.py` to accept and use `PromptRegistry`
- [x] 2.3 Update component setup in `muggle/app.py` to initialize `PromptRegistry` and inject it into `ChatProcessor`
- [x] 2.5 Update `muggle/app.py` imports to use `muggle.registry`
- [x] 2.6 Update `tests/test_registry.py` to test for `PromptNotFoundError`

## 3. Verification

- [x] 3.1 Run existing unit tests and ensure they pass with new structure
- [x] 3.2 Add a specific test case for `PromptNotFoundError` message content
- [x] 3.3 Verify application startup and basic chat functionality
