## 1. Preparation & Structure

- [x] 1.1 Create `src/muggle` and layered subdirectories (`core`, `infra`, `api`, `shared`).
- [x] 1.2 Move code files to their new homes:
    - `muggle/ai.py` -> `src/muggle/core/processor.py`
    - `muggle/exceptions.py` -> `src/muggle/core/exceptions.py`
    - `muggle/config.py` -> `src/muggle/infra/config.py`
    - `muggle/registry/` -> `src/muggle/infra/registry/`
    - `muggle/app.py` -> `src/muggle/app.py`
    - `muggle/blueprints/` -> `src/muggle/blueprints/`
    - `muggle/static/` -> `src/muggle/static/`
    - `muggle/utils.py` -> `src/muggle/shared/utils.py`
    - `muggle/__init__.py` -> `src/muggle/__init__.py`
- [x] 1.3 Move `prompts/` to `src/muggle/infra/prompts/`.
- [x] 1.4 Delete the original `muggle/` directory after verifying all files moved.

## 2. Code Updates

- [x] 2.1 Update `pyproject.toml` with `packages` configuration and update the `muggle` script entrypoint.
- [x] 2.2 Perform global find-and-replace for internal imports across all files in `src/` and `tests/`.
- [x] 2.3 Update `src/muggle/app.py` to calculate `static_folder` path relative to `__file__`.
- [x] 2.4 Refactor `src/muggle/infra/registry/prompt.py` to use `importlib.resources` for loading prompts.

## 3. Tooling & Docs

- [x] 3.1 Update PyCharm run configuration in `.run/app.run.xml` to point to the new app location.
- [x] 3.2 Update PyCharm project structure in `.idea/muggle.iml` to mark `src` as the source root.
- [x] 3.3 Update `README.md` with correct usage instructions (fixing `main.py` reference).
- [x] 3.4 Update `GEMINI.md` to reflect the new project structure and layered architecture.

## 4. Verification

- [x] 4.1 Run `poetry install` to synchronize the virtual environment with the new `src` layout.
- [x] 4.2 Run `poetry run pytest` to verify all components and tests are working with the new structure.
- [x] 4.3 Manually verify the Flask application starts via `poetry run muggle`.
