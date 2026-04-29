## Why

The current `muggle` codebase uses a flat layout where core AI logic, web infrastructure, and configuration management are all mixed at the root level. This makes the project difficult to maintain, prone to circular imports, and complicated to package or distribute as a library. Moving to a standard `src` layout with a strictly layered architecture (Brain, Plumbing, Face) will improve modularity, isolation, and professional quality.

## What Changes

- **BREAKING**: Reorganize the project into a `src` layout. All source code will move from `muggle/` to `src/muggle/`.
- **BREAKING**: Reorganize the package into a layered architecture:
    - `muggle.core`: Pure AI logic (formerly `ai.py`).
    - `muggle.infra`: Configuration and registries (formerly `config.py` and `registry/`).
    - `muggle.app`: Flask application entry point, routes, and static assets (formerly `app.py`, `blueprints/`, and `static/`).
    - `muggle.shared`: General utilities (formerly `utils.py`).
- **BREAKING**: Relocate `prompts/` to `src/muggle/infra/prompts/` and implement `importlib.resources` for internal prompt loading.
- **Update**: Update `pyproject.toml` to reflect the new `src` layout and entry points.
- **Update**: Synchronize IDE configurations (PyCharm `.run` files and `.idea` settings).
- **Update**: Update project documentation (`README.md`, `GEMINI.md`) and all tests.

## Capabilities

### New Capabilities
- None (Structural reorganization).

### Modified Capabilities
- None (Behavioral requirements remain unchanged, only implementation structure is refactored).

## Impact

- **Imports**: All internal imports will change (e.g., `from muggle.ai import ...` -> `from muggle.core.processor import ...`).
- **Packaging**: The project will now require an "editable install" (`pip install -e .` or `poetry install`) for local development.
- **Data Loading**: Prompts will now be loaded via package resources rather than direct filesystem paths by default.
- **Tooling**: IDEs and CLI scripts (like `poetry run muggle`) must be updated to find the new entry points.
