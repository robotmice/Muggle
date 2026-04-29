## ADDED Requirements

### Requirement: Internal Prompt Discovery
The system MUST be able to discover and load prompts from within the package structure using `importlib.resources`.

#### Scenario: Loading from package
- **WHEN** the `PromptRegistry` is initialized
- **THEN** it MUST default to searching for prompts within the `muggle.infra.prompts` package resources.
