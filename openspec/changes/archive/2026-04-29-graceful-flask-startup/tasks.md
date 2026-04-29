## 1. AI Layer Enhancements

- [x] 1.1 Implement `ModelRegistry` in `muggle/registry.py`.
- [x] 1.2 Update `ChatProcessor` to retrieve models from the `ModelRegistry`.
- [x] 1.3 Add a `is_initialized()` property or method to `ChatProcessor` to verify internal state.
- [x] 1.4 Implement a `warm_up()` method in `ChatProcessor` to ensure internal resources are ready.

## 2. Flask Application Refactoring

- [x] 2.1 Create the `muggle/blueprints/` package with `__init__.py`.
- [x] 2.2 Implement `muggle/blueprints/chat.py` and `muggle/blueprints/monitoring.py`.
- [x] 2.3 Refactor `muggle/app.py` to implement the `create_app()` factory function.
- [x] 2.4 Register blueprints in `create_app()` using the `muggle/blueprints` registration helper.
- [x] 2.5 Move component initialization (e.g., `ChatProcessor`) into the application factory context.
- [x] 2.6 Update the `run()` function to use `create_app()` and `ConfigManager` for server settings.

## 3. Configuration Updates

- [x] 3.1 Update `config.toml` to include server settings (host, port, debug mode).
- [x] 3.2 Update `muggle/config.py` to provide access to server settings.

## 4. Verification and Testing

- [x] 4.1 Create `tests/test_app.py` to verify the application factory and health check endpoint.
- [x] 4.2 Verify that the application starts up correctly and performs the warm-up sequence.
- [x] 4.3 Ensure all existing tests pass with the new factory pattern.
