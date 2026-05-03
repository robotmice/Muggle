## Context

The codebase contains Pydantic models that use a mix of annotation styles. Pydantic V2 and modern tooling recommend a unified style for clarity and to prevent introspection issues with libraries like LangGraph.

## Goals / Non-Goals

**Goals:**
- Refactor all Pydantic models to consistently use the `xxx: Annotated[xxx] = Field(xxx)` style.

**Non-Goals:**
- Introduce any functional changes to the models.
- Change any data types or validation rules.

## Decisions

- **Decision 1: Adopt Unified Pydantic V2 Style**: All Pydantic model fields using `Annotated` will be updated to the `xxx: Annotated[xxx] = Field(xxx)` format.
  - *Rationale*: This is the recommended astyle in Pydantic V2 documentation, and it resolves ambiguity that has caused issues with LangGraph's state management.

## Risks / Trade-offs

- None. This is a low-risk, non-functional refactoring.
