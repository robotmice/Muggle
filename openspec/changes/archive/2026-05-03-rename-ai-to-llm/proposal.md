## Why

The term 'AI' is overly broad and often confusing in technical contexts. In this system, we are specifically working with Large Language Models (LLMs) and structured models. Renaming 'AI' to 'LLM' or 'Model' will provide better technical precision and align with the project's actual implementation (LangChain, LangGraph).

## What Changes

- Rename `ai-processor` capability to `llm-processor`.
- **BREAKING**: Update configuration key `ai` to `llm` in `config.toml`.
- Update class names, variables, and log messages from `AI` to `LLM` or `Model` (e.g., `ai_config` -> `llm_config`, `AI Processor` -> `LLM Processor`).
- Update frontend CSS and JavaScript to use `llm` instead of `ai` (e.g., class `.ai` -> `.llm`).
- Consolidate redundant specifications between `ai-processor` and `llm-processor`.
- Update all documentation (README.md, GEMINI.md, and other markdown files) to use precise 'LLM' or 'Model' terminology.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `ai-processor`: Being renamed and consolidated into `llm-processor`.
- `llm-processor`: Updating requirements to use precise 'LLM' terminology.
- `model-configuration`: Updating configuration schema to use `llm` instead of `ai`.
- `chat-api`: Updating error messages and internal terminology.

## Impact

- **Configuration**: Users must update `config.toml` to use the `[llm]` section.
- **Codebase**: Wide-ranging rename across core, infra, and api layers.
- **Documentation**: Updates required in README.md, GEMINI.md, and spec files.
- **Frontend**: Minor CSS/JS updates.
- **Specs**: Removal of `ai-processor` and refinement of `llm-processor`.
