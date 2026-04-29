## Context

The `muggle` project currently resides in a flat layout where all modules are at the root level of the `muggle/` directory. This mixes infrastructure, web API, and core logic, making it difficult to scale and package. This design refactors the project into a professional `src` layout with clearly defined layers.

## Goals / Non-Goals

**Goals:**
- Move to a `src` layout (`src/muggle/`).
- Establish a layered architecture: `core`, `infra`, `api`, and `shared`.
- Use `importlib.resources` for internal prompt management.
- Ensure all developer tooling (PyCharm, Poetry) continues to work seamlessly.
- Maintain existing API behavior and endpoint structure.

**Non-Goals:**
- Adding new AI features or agents.
- Refactoring the internal logic of the `ChatProcessor` or `Registry` classes beyond structural changes.
- Changing the configuration schema in `config.toml`.

## Decisions

### 1. The "src" Layout
We will move the `muggle/` package into a `src/` subdirectory.
- **Rationale**: This is the recommended layout for modern Python projects. It prevents accidental imports of the local source tree and ensures that the package is properly installed before testing.
- **Alternative**: Keep the flat layout. Rejected because it doesn't solve the "unorganized" feeling and is less professional for packaging.

### 2. Layered Package Structure
We will divide the `muggle` package into specific layers:
- `muggle.core`: Contains the "Brain" of the application (`processor.py`, `exceptions.py`).
- `muggle.infra`: Contains the "Plumbing" (`config.py`, `registry/`, `prompts/`).
- `muggle.app`: Contains the entry point and Flask logic (`app.py`, `blueprints/`, `static/`).
- `muggle.shared`: Contains general-purpose helpers (`utils.py`).
- **Rationale**: Strict separation of concerns allows for easier testing and prevents circular dependencies.

### 3. Prompt Management via Package Resources
Prompts will move from the root `prompts/` directory to `src/muggle/infra/prompts/`.
- **Rationale**: Treating prompts as package data ensures the application is self-contained. Using `importlib.resources` is the modern, platform-independent way to access these files.
- **Alternative**: Keep prompts at the root. Rejected as it makes the package less portable.

### 4. Flask Static Asset Pathing
In `src/muggle/app.py`, the `static_folder` will be defined relative to the file's location.
- **Rationale**: Since the file is moving deeper into the package, hardcoded paths like `'static'` would break. Using `__file__` ensures robustness.

## Risks / Trade-offs

- **[Risk] Broken Imports** → **Mitigation**: Perform a global regex-based find and replace followed by manual verification and running the full test suite.
- **[Risk] IDE/CLI breakage** → **Mitigation**: Update `pyproject.toml` (packages and scripts), `.run/app.run.xml`, and `.idea/muggle.iml` as part of the implementation.
- **[Risk] Test failures due to pathing** → **Mitigation**: Update tests to use the new package structure for imports and adjust any tests that mock file system access.
