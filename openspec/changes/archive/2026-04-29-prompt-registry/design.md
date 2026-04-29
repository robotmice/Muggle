## Context

The `muggle` project currently lacks a structured way to manage prompts. By introducing a `PromptRegistry`, we allow prompts to be treated as assets rather than hardcoded strings. This aligns with the project's goal of being AI-native and spec-driven.

## Goals / Non-Goals

**Goals:**
- Provide a `PromptRegistry` class in `muggle/registry.py`.
- Support Markdown files with YAML frontmatter.
- Support Jinja2 templating for all prompts.
- Integrate with `ConfigManager` to allow path configuration via `config.toml`.
- Provide typed accessors (`get_system_prompt`, `get_user_prompt`) using a `variables` dictionary for substitution.

**Non-Goals:**
- Implementing a web UI for prompt editing.
- Supporting nested directory structures for prompt discovery (initial version will be flat or single-level).
- Automated prompt versioning or A/B testing logic.

## Decisions

### 1. File Organization: Type-Based Subfolders
- **Rationale**: Storing prompts in folders like `system/` and `user/` provides a clear, file-system-based hierarchy. The folder name implicitly defines the prompt type, reducing the need for mandatory metadata inside the file for type identification.
- **Alternatives**: Flat folder with frontmatter (requires more parsing logic for indexing).

### 2. File Format: Markdown
- **Rationale**: Markdown is human-readable and works well with existing LLM development tools. Frontmatter (YAML) can still be used for additional metadata (like description or variables), but the type is determined by the folder.
- **CRISPE Standard**: All system prompts will follow the CRISPE principle (Capacity, Insight, Statement, Personality, Experiment) to ensure high-quality and consistent AI behavior. An `example.md` will be provided as the gold standard.

### 3. Templating Engine: Jinja2
- **Rationale**: Jinja2 is the industry standard for Python templating. It is already widely used in LangChain ecosystems and provides superior flexibility compared to f-strings (loops, conditionals, filters).
- **Alternatives**: Python f-strings (limited); custom regex replacement (reinventing the wheel).

### 3. Registry Pattern: Lazy Indexing
- **Rationale**: The registry will scan the directory on initialization to map names to files and types, but it will only load and parse the content when requested (lazy loading). This keeps startup fast.

### 4. Integration with ConfigManager
- **Rationale**: Centralizing the prompt path in `config.toml` follows the existing pattern in the project for server and AI settings.

## Risks / Trade-offs

- **[Risk] Path Misconfiguration** → **Mitigation**: `PromptRegistry` will check for directory existence and raise a clear error if the path is invalid.
- **[Risk] Jinja2 Syntax Errors** → **Mitigation**: Error handling during the `render` call will provide descriptive messages to help debug prompt templates.
- **[Trade-off] Metadata Rigidity** → We enforce `type` in frontmatter. If a file is missing frontmatter, it will be ignored or raise an error to ensure system integrity.
