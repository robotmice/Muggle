## MODIFIED Requirements

### Requirement: Typed Prompt Access
The registry MUST provide typed accessors that look for prompts within their corresponding subfolders.

#### Scenario: Valid type access
- **WHEN** `get_system_prompt("translator")` is called
- **THEN** the registry MUST look for the file in the `system/` subfolder and return the rendered content.

#### Scenario: Missing prompt access
- **WHEN** `get_system_prompt("nonexistent")` is called
- **THEN** the registry MUST raise a `PromptNotFoundError` indicating the specific prompt and type that were missing.
