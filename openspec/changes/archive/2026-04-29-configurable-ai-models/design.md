## Context

Currently, AI model parameters are hardcoded in `muggle/ai.py` using the `ChatDeepSeek` class directly. Environment variables are managed implicitly. This design introduces a centralized configuration utility and leverages LangChain's `init_chat_model` for standardized model initialization.

## Goals / Non-Goals

**Goals:**
- Centralize all configuration management (environment variables and model settings) in `muggle/config.py`.
- Support TOML-based configuration for AI model parameters.
- Ensure the `.env` file is loaded automatically by the configuration utility.
- Refactor `ChatProcessor` to use `init_chat_model` driven by the centralized configuration.

**Non-Goals:**
- Implementing a full-featured CLI for configuration management.
- Migrating non-AI related settings to the new utility (out of scope unless necessary for AI setup).

## Decisions

### 1. Configuration Storage: TOML
- **Choice**: Use `config.toml` for model-specific settings (model name, provider, temperature).
- **Rationale**: TOML is more readable and structured than `.env` for complex configurations like model parameters.
- **Parsing**: Use the standard library `tomllib` (available in Python 3.11+).

### 2. Configuration Utility: `ConfigManager` Class
- **Choice**: Create a `ConfigManager` class in `muggle/config.py`.
- **Implementation**: It will handle `load_dotenv()` and provide methods/properties to access model settings.
- **Rationale**: Encapsulates configuration logic and provides a single source of truth.

### 3. Model Initialization: `init_chat_model`
- **Choice**: Use `langchain.chat_models.init_chat_model` in `ChatProcessor`.
- **Rationale**: `init_chat_model` is a factory function that simplifies model instantiation and makes it easier to switch between different providers (e.g., DeepSeek, OpenAI, Anthropic) by simply changing the configuration.

## Risks / Trade-offs

- **[Risk]** → Missing environment variables for specific providers.
  - **Mitigation**: The `ConfigManager` should validate that required environment variables (e.g., `DEEPSEEK_API_KEY`) are present for the configured provider.
- **[Risk]** → `init_chat_model` requires specific provider packages.
  - **Mitigation**: Ensure relevant packages (like `langchain-deepseek`) are listed in `pyproject.toml`.
