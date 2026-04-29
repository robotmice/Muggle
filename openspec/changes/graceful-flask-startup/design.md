## Context

The current Flask application in `muggle/app.py` initializes a global `ChatProcessor` instance and uses a simple `app.run()` in the `run()` function. This "script-style" startup is difficult to test (global state) and doesn't handle initialization failures or warm-up needs (e.g., verifying the AI model is responsive).

## Goals / Non-Goals

**Goals:**
- Implement the **Application Factory Pattern** (`create_app()`).
- Decouple component initialization from module import.
- Add a `/health` endpoint for readiness/liveness checks.
- Support a "warm-up" phase during startup.
- Use `ConfigManager` for all server settings (host, port, debug).

**Non-Goals:**
- Migrating to a different web framework (e.g., FastAPI).
- Implementing complex background worker queues (out of scope for startup/warm-up).

## Decisions

### 1. Application Factory Pattern
- **Choice**: Refactor `muggle/app.py` to contain a `create_app(config_name=None)` function.
- **Rationale**: Standard Flask best practice. Allows creating multiple app instances with different configs (e.g., for testing). Prevents side effects during import.

### 2. Modularization: Flask Blueprints Package
- **Choice**: Organize Blueprints into a dedicated `muggle/blueprints/` package.
  - `muggle/blueprints/chat.py`: Contains `chat_bp`.
  - `muggle/blueprints/monitoring.py`: Contains `monitor_bp`.
  - `muggle/blueprints/__init__.py`: Provides a `register_blueprints(app)` helper.
- **Rationale**: Decouples routing logic from the main application entry point. Following a package structure makes the project easier to navigate and scale as more features are added.

### 3. Model Registry Pattern
- **Choice**: Implement a `ModelRegistry` class in `muggle/registry.py`.
- **Implementation**: It will store model configurations (provider, id, params) and handle lazy instantiation via `init_chat_model`.
- **Rationale**: Centralizes model management. Allows the system to support multiple models, handle aliasing (e.g., "primary-chat"), and provides a clean interface for `ChatProcessor` and other components to retrieve model instances.

### 4. Component Initialization
- **Choice**: Move `ChatProcessor` initialization into a `setup_components(app)` function called by `create_app`.
- **Rationale**: Ensures dependencies are initialized within the application context.

### 3. Health Check and Warm-up
- **Choice**: Add a `/health` route that checks the initialization state of application components. The `warm_up()` method in `ChatProcessor` will focus on internal resource allocation and configuration validation.
- **Rationale**: Decouples application liveness from external provider availability. The `/health` endpoint confirms the server is correctly configured and ready to handle requests, even if an external provider is experiencing temporary issues.

### 4. CLI Entrypoint
- **Choice**: The `run()` function in `muggle/app.py` will use `create_app()` and pull `host`/`port`/`debug` from `ConfigManager` or environment variables.
- **Rationale**: Keeps the entry point clean and configurable.

## Risks / Trade-offs

- **[Risk]** → Warm-up takes too long, causing timeouts.
  - **Mitigation**: Implement a timeout for the warm-up phase and allow the app to start in a "degraded" state (unhealthy `/health`) rather than blocking indefinitely.
- **[Risk]** → Circular imports when components need the `app` instance.
  - **Mitigation**: Use Flask's `current_app` proxy where possible.
