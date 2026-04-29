## Why

AI model configuration is currently hardcoded within the `ChatProcessor` class, and environment variable management is decentralized. This makes it difficult to switch models, manage settings across different environments, or extend the system with new models without modifying core logic.

## What Changes

- **TOML Configuration**: Introduce a `config.toml` file to define AI model parameters (provider, model name, temperature, etc.).
- **Configuration Utility**: Create a dedicated utility class to parse the TOML file and manage environment variables (including `.env` loading).
- **Standardized Initialization**: Refactor AI model initialization to use LangChain's `init_chat_model` factory function, driven by the configuration utility.
- **Environment Management**: Centralize `.env` file management within the configuration utility.

## Capabilities

### New Capabilities
- `model-configuration`: Centralized management of AI model settings and environment variables via TOML and a utility class.

### Modified Capabilities
- `ai-processor`: Update the AI processing logic to initialize models using the new configuration utility and `init_chat_model`.

## Impact

- `muggle/ai.py`: Initialization logic will be refactored.
- New file `muggle/config.py`: Configuration utility class.
- New file `config.toml`: Model settings.
- `muggle/app.py` or entry points: May need to call the config utility.
- Dependencies: LangChain (for `init_chat_model`).
