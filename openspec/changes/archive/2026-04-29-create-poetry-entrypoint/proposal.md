## Why

The project currently lacks a formal entry point, requiring users to run the application using `poetry run python muggle/app.py`. Implementing a Poetry script entrypoint will provide a more professional CLI experience and simplify application startup.

## What Changes

- Add a `run()` function to `muggle/app.py` to encapsulate the application startup logic.
- Configure `pyproject.toml` to include a `muggle` script that points to the new `run()` function.
- Update `README.md` (optional but recommended) to reflect the new way to run the application.

## Capabilities

### New Capabilities
- `cli-entrypoint`: Provides a dedicated command-line command to start the Flask application.

### Modified Capabilities
- None

## Impact

- `pyproject.toml`: Addition of `[tool.poetry.scripts]` entry.
- `muggle/app.py`: Addition of a `run` function.
- Development workflow: Users can now use `poetry run muggle` to start the server.
