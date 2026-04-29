## 1. Preparation & Configuration

- [x] 1.1 Add `jinja2` and `pyyaml` to dependencies in `pyproject.toml` (if not present)
- [x] 1.2 Update `muggle/config.py` to support `[prompts]` section in `ConfigManager`
- [x] 1.3 Update `config.toml` with default prompt registry path
- [x] 1.4 Create initial `prompts/` directory for testing

## 2. Prompt Registry Implementation

- [x] 2.1 Implement frontmatter parsing utility (YAML extraction)
- [x] 2.2 Implement `PromptRegistry` class in `muggle/registry.py`
- [x] 2.3 Implement directory scanning for type-based subfolders (`system/`, `user/`)
- [x] 2.4 Implement Jinja2 template rendering logic
- [x] 2.5 Implement typed accessors: `get_system_prompt`, `get_user_prompt`
- [x] 2.9 Refactor accessors to use `variables: dict` instead of `**kwargs`
- [x] 2.6 Implement error handling for missing prompts in subfolders
- [x] 2.7 Create `prompts/system/example.md` following CRISPE principle
- [x] 2.8 Identify and migrate existing hardcoded prompts to `prompts/` subfolders

## 3. Testing & Verification

- [x] 3.1 Create unit tests for frontmatter parsing
- [x] 3.2 Create unit tests for `PromptRegistry` discovery and indexing
- [x] 3.3 Create unit tests for Jinja2 rendering with variables
- [x] 3.4 Verify type validation logic with negative test cases
- [x] 3.5 Verify CRISPE example loads and renders correctly
- [x] 3.6 End-to-end verification: Load a sample prompt and render it
