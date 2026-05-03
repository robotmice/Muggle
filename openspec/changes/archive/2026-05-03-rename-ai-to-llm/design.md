## Context

The current codebase uses the term 'AI' generically for LLM-related components. This creates ambiguity and doesn't align with modern terminology or the project's focus on LLMs and structured models. There is also redundancy in the specifications (`ai-processor` vs `llm-processor`).

## Goals / Non-Goals

**Goals:**
- Replace 'AI' with 'LLM' or 'Model' across all layers (Core, Infra, API, Frontend).
- Update configuration keys to be more precise.
- Consolidate redundant specifications.
- Update all project documentation to reflect the new terminology.
- Maintain backward compatibility where possible, but allow breaking changes in config.

**Non-Goals:**
- Changing the underlying logic or framework (LangChain/LangGraph).
- Refactoring unrelated parts of the codebase.

## Decisions

### 1. Configuration Key Rename
**Decision**: Rename `[ai]` section in `config.toml` to `[llm]`.
**Rationale**: Aligns with the move towards more precise terminology.
**Alternatives**: 
- `[model]`: Too generic as we might have non-LLM models later.
- Keep `[ai]`: Maintains ambiguity we are trying to solve.

### 2. Capability Consolidation
**Decision**: Remove `ai-processor` and move all requirements to `llm-processor`.
**Rationale**: Simplifies the spec-driven workflow by having a single source of truth for the primary processing logic.

### 3. Variable and Class Renaming
**Decision**: Systematically rename `ai_*` variables and `AI*` classes to `llm_*` and `LLM*`.
**Rationale**: Consistency across the codebase.
**Risk**: Missing some occurrences in string literals or dynamic lookups.
**Mitigation**: Use project-wide grep and verify with existing tests.

## Risks / Trade-offs

- **[Risk]**: Breaking existing user configurations. → **Mitigation**: Update `.env.example` and provide a clear migration note in the proposal.
- **[Risk]**: Regression in functionality due to renaming. → **Mitigation**: Run existing test suite (`pytest`) after each major rename phase.
- **[Risk]**: Frontend styling break if CSS classes are renamed. → **Mitigation**: Update both `index.html` and the backend `jsonify` calls simultaneously.
