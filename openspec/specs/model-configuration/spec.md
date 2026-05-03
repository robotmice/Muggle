# Capability: model-configuration

## Purpose
TBD - Manages the configuration of LLM models and application settings.

## Requirements

### Requirement: Centralized Configuration Management
The system SHALL provide a dedicated utility class to manage application configuration, including environment variables and LLM model settings.

#### Scenario: Environment Variable Loading
- **WHEN** the configuration utility is initialized
- **THEN** it SHALL automatically load variables from the `.env` file

#### Scenario: TOML Configuration Loading
- **WHEN** the configuration utility is initialized
- **THEN** it SHALL load LLM model settings from a `config.toml` file under the `[llm]` section.

### Requirement: Standardized Model Parameters
The configuration utility SHALL provide access to LLM model parameters (provider, model name, temperature, etc.) in a structured format suitable for `init_chat_model`.

#### Scenario: Retrieval of model settings
- **WHEN** the configuration utility is queried for LLM settings
- **THEN** it returns the provider, model name, and other relevant parameters as defined in the TOML file
