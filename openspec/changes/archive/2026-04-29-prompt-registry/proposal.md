## Why

Currently, AI prompts are hardcoded or managed informally, making them difficult to version, audit, and modify without code changes. We need a centralized, metadata-driven registry to manage prompts as independent Markdown files with clearly defined types (system, user).

## What Changes

- **Prompt Organization**: Prompts will be stored in subfolders named after their type (e.g., `system/`, `user/`).
- **CRISPE Principle**: System prompts MUST follow the CRISPE principle (Capacity, Insight, Statement, Personality, Experiment).
- **Example Template**: An `example.md` file will be provided in the `system/` folder as a reference.
- **Migration**: Any hardcoded prompt logic will be migrated to the Markdown registry.
- **Markdown-based Prompts**: Prompts will be stored as `.md` files where the filename is the registration key.
- **Dynamic Templating**: Support for variable injection using Jinja2 within the Markdown templates.
- **Registry API**: Clean methods like `get_system_prompt(name, **kwargs)` for accessing prompts from their respective type folders.

## Capabilities

### New Capabilities
- `prompt-registry`: Core logic for scanning, loading, and serving prompts from Markdown files.
- `prompt-templating`: Logic for parsing frontmatter and rendering Jinja2 templates with input variables.

### Modified Capabilities
- `model-configuration`: Update configuration to include settings for the prompt registry path.

## Impact

- `muggle/registry.py`: Addition of the `PromptRegistry` class.
- `muggle/config.py`: Update to `ConfigManager` to handle prompt settings.
- `config.toml`: New `[prompts]` section.
- `muggle/ai.py`: Future integration for `ChatProcessor` to use the registry.
