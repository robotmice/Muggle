## Why

While Python 3.3+ supports implicit namespace packages, the `muggle` project relies on `importlib.resources` for loading prompts and follows a structured `src` layout. Missing `__init__.py` files in several key directories (`core`, `infra`, `shared`, `prompts`) can lead to:
1. **Unreliable Resource Loading**: `importlib.resources` is more robust when dealing with explicit packages.
2. **Tooling Friction**: IDEs, linters, and type checkers (like MyPy) may fail to correctly resolve imports or identify package boundaries.
3. **Inconsistency**: Currently, some folders have `__init__.py` while others don't, creating confusion.

Adding these package markers will "button up" the recent reorganization and ensure a professional, standard-compliant Python package.

## What Changes

- **Add**: Create `__init__.py` files in the following directories:
    - `src/muggle/core/`
    - `src/muggle/infra/`
    - `src/muggle/infra/prompts/`
    - `src/muggle/infra/prompts/system/`
    - `src/muggle/infra/prompts/user/`
    - `src/muggle/shared/`
- **Verify**: Ensure that all existing imports and resource loading continue to function correctly.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- **Package Integrity**: Improved consistency and tool support for the package structure.

## Impact

- **Minimal**: This is a non-breaking structural improvement. It will not change existing logic but will make the package more robust and standard-compliant.
