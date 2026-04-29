# Design: Finalize Package Structure

## Problem Statement
The current `src` layout implementation is incomplete because it relies on implicit namespace packages for several core components. This deviates from standard Python best practices for applications of this complexity and can cause issues with resource discovery and static analysis.

## Decision: Explicit Package Markers
We will add empty `__init__.py` files to all directories within `src/muggle/` that are intended to be part of the package.

### Target Directories
1. `src/muggle/core`: Contains the "Brain" of the application.
2. `src/muggle/infra`: Contains "Plumbing" like config and registries.
3. `src/muggle/infra/prompts`: Central storage for AI prompts.
4. `src/muggle/infra/prompts/system`: System-level prompts.
5. `src/muggle/infra/prompts/user`: User-level prompts.
6. `src/muggle/shared`: Utility functions.

## Rationale
- **Predictability**: Explicit `__init__.py` files make it clear to both Python and developers that a directory is a package.
- **Resource Access**: `importlib.resources` functions more reliably when the target is an established package.
- **Standards**: Most professional Python projects (and library templates) use explicit package markers.

## Verification Plan
1. **Creation**: Confirm all files are created.
2. **Resource Loading**: Run a script/test that loads a prompt from `muggle.infra.prompts` to ensure `importlib.resources` still functions correctly.
3. **Execution**: Run `poetry run muggle` to ensure the application starts without import errors.
4. **Tests**: Run `poetry run pytest` to ensure no regressions in the test suite.
