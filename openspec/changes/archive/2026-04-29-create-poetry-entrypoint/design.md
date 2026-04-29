## Context

The application currently lacks a formal entry point in the package structure. While it can be run as a script (`python muggle/app.py`), this doesn't leverage Poetry's ability to create executable commands.

## Goals / Non-Goals

**Goals:**
- Enable `poetry run muggle` as the primary way to start the application.
- Maintain backward compatibility for running `python muggle/app.py` directly.

**Non-Goals:**
- Refactoring the entire application structure.
- Changing the underlying Flask configuration or AI processing logic.

## Decisions

### 1. Add `run()` function to `muggle/app.py`
We will introduce a `run()` function in `muggle/app.py` that calls `app.run()`.
- **Rationale**: Provides a clean entry point for Poetry's script mechanism.
- **Alternatives**: Pointing Poetry directly to `muggle.app:app.run` (less flexible for future initialization steps).

### 2. Configure `[tool.poetry.scripts]` in `pyproject.toml`
Add a mapping from `muggle` to `muggle.app:run`.
- **Rationale**: Standard Poetry practice for creating CLI shortcuts.

## Risks / Trade-offs

- **Risk**: Environment variables (like those in `.env`) might not be loaded if the entry point bypasses the `load_dotenv()` call in `app.py`.
- **Mitigation**: Ensure `load_dotenv()` is called at the module level or within the `run()` function. In the current `app.py`, it is called at the module level, which is sufficient.
