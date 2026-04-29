## 1. Configuration Setup

- [x] 1.1 Create `config.toml` with default AI model settings (provider, model, temperature).
- [x] 1.2 Implement `ConfigManager` in `muggle/config.py` using `tomllib`.
- [x] 1.3 Ensure `ConfigManager` calls `load_dotenv()` from `python-dotenv`.
- [x] 1.4 Add methods to `ConfigManager` to retrieve AI model settings.

## 2. AI Processor Refactoring

- [x] 2.1 Update `muggle/ai.py` to import and use `ConfigManager`.
- [x] 2.2 Refactor `ChatProcessor.__init__` to use `init_chat_model` with parameters from `ConfigManager`.

## 3. Verification and Testing

- [x] 3.1 Create `tests/test_config.py` to verify `ConfigManager` loads settings from TOML and environment variables.
- [x] 3.2 Update `tests/test_ai.py` to mock `init_chat_model` and verify the refactored `ChatProcessor`.
- [x] 3.3 Run all tests to ensure no regressions.
