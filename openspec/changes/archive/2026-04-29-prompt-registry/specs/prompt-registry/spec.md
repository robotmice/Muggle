## ADDED Requirements

### Requirement: Prompt Registry Discovery
The system MUST scan type-based subfolders (e.g., `system/`, `user/`) within a configurable root directory for `.md` files and register them as prompts.

#### Scenario: Registering prompts from subfolders
- **WHEN** the `PromptRegistry` is initialized with a path containing `system/translator.md` and `user/refiner.md`
- **THEN** the registry MUST index both files, associating "translator" with the "system" type and "refiner" with the "user" type.

### Requirement: Typed Prompt Access
The registry MUST provide typed accessors that look for prompts within their corresponding subfolders.

#### Scenario: Valid type access
- **WHEN** `get_system_prompt("translator")` is called
- **THEN** the registry MUST look for the file in the `system/` subfolder and return the rendered content.

#### Scenario: Missing prompt access
- **WHEN** `get_system_prompt("nonexistent")` is called
- **THEN** the registry MUST raise a `FileNotFoundError` or similar clear error.

### Requirement: CRISPE Principle Compliance
All system prompts MUST be structured according to the CRISPE principle.

#### Scenario: CRISPE validation (manual/informal)
- **WHEN** a system prompt is created
- **THEN** it SHOULD contain sections or logic addressing Capacity, Insight, Statement, Personality, and Experiment.

### Requirement: Default CRISPE Example
The system MUST provide an `example.md` in the `system/` subfolder that demonstrates the CRISPE principle.

#### Scenario: Accessing the example
- **WHEN** `get_system_prompt("example")` is called
- **THEN** it MUST return the content of the CRISPE-compliant `example.md`.

### Requirement: Variable Injection with Jinja2
The registry MUST support variable injection using Jinja2 syntax within the prompt templates.

#### Scenario: Rendering with variables
- **WHEN** `get_system_prompt("translator", variables={"language": "French"})` is called
- **AND** the template contains "Translate to {{language}}"
- **THEN** the returned string MUST be "Translate to French".
