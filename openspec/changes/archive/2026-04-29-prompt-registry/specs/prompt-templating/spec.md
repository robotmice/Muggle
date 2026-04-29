## ADDED Requirements

### Requirement: Frontmatter Parsing
The system MUST parse YAML frontmatter from Markdown files to extract metadata such as `type`.

#### Scenario: Successful frontmatter extraction
- **WHEN** a file starts with `---` followed by `type: system` and `---`
- **THEN** the system MUST extract `system` as the prompt type and the remaining text as the template.

### Requirement: Template Rendering
The system MUST use Jinja2 to render templates, supporting basic variable substitution, conditionals, and filters.

#### Scenario: Complex rendering
- **WHEN** a template contains `{% if name %}Hello {{name}}{% else %}Hello stranger{% endif %}`
- **AND** `render(name="Alice")` is called
- **THEN** the output MUST be "Hello Alice".
