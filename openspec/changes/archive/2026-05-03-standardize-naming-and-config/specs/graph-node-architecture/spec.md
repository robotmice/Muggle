## MODIFIED Requirements

### Requirement: Pipeline-Stage Sub-Package Layout

Graph nodes SHALL be organized into sub-packages under `src/muggle/core/` grouped by pipeline stage:

| Stage       | Sub-package | Nodes                              |
|-------------|-------------|------------------------------------|
| Guard       | `guard/`    | intent_check, fallback             |
| Memory      | `memory/`   | summarize                          |
| Search      | `search/`   | query_rewrite, retrieval           |
| Response    | `response/` | inquiry                            |
| Validation  | (root)      | validation                         |

Each sub-package MUST be a valid Python package containing an `__init__.py` and MAY export its node class(es).

#### Scenario: Importing a node from its stage package

- **WHEN** `GraphProcessor` needs the intent check node
- **THEN** it SHALL import it as `from muggle.core.guard import IntentCheckNode`

### Requirement: Standard Node Contract

Every graph node SHALL be implemented as a class with dependencies received in `__init__` and state transformation in `__call__`. The `__call__` method MUST accept a `state` parameter matching the graph's state schema and a `config` parameter of type `RunnableConfig`, returning a `dict` of state field updates.

#### Scenario: Node with model and prompt dependencies

- **WHEN** a node (e.g., intent check) requires an LLM model and a system prompt
- **THEN** it MUST receive the model and `PromptRegistry` via its constructor
- **AND** its `__call__` method MUST accept `(state, config)` and return a state update dict

#### Scenario: Node with no dependencies

- **WHEN** a node (e.g., fallback response) requires no external dependencies
- **THEN** it MUST still be implemented as a class conforming to the `(state, config) -> dict` contract

#### Scenario: LangGraph invokes node with config

- **WHEN** the compiled graph executes a node
- **THEN** it SHALL invoke the node's `__call__` method with both the current state and the runnable config
