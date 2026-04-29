## 1. Structural Changes

- [ ] 1.1 Create `muggle/registry/` package directory with `__init__.py`
- [ ] 1.2 Create `muggle/exceptions.py` with `MuggleError` and `PromptNotFoundError`
- [ ] 1.3 Move `ModelRegistry` from `muggle/registry.py` to `muggle/registry/model.py`
- [ ] 1.4 Move `PromptRegistry` from `muggle/registry.py` to `muggle/registry/prompt.py`
- [ ] 1.5 Update `muggle/registry/__init__.py` to export both registries
- [ ] 1.6 Remove the old `muggle/registry.py` file

## 2. Implementation Refinement

- [ ] 2.1 Update `PromptRegistry` to raise `PromptNotFoundError` instead of `FileNotFoundError`
- [ ] 2.2 Update `muggle/ai.py` imports to use `muggle.registry`
- [ ] 2.3 Update `muggle/app.py` imports to use `muggle.registry`
- [ ] 2.4 Update `tests/test_registry.py` to test for `PromptNotFoundError`

## 3. Verification

- [ ] 3.1 Run existing unit tests and ensure they pass with new structure
- [ ] 3.2 Add a specific test case for `PromptNotFoundError` message content
- [ ] 3.3 Verify application startup and basic chat functionality
