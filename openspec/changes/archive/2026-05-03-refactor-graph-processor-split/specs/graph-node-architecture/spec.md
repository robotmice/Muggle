## ADDED Requirements

### Requirement: Standard Node Contract

Every graph node SHALL be implemented as a class with dependencies received in `__init__` and state transformation in `__call__`. The `__call__` method MUST accept a `state` parameter matching the graph's state schema and a `config` parameter of type `RunnableConfig`, returning a `dict` of state field updates.

#### Scenario: Node with model and prompt dependencies

- **WHEN** a node (e.g., intent check) requires an LLM model and a system prompt
- **THEN** it MUST receive the model and `PromptRegistry` via its constructor
- **AND** its `__call__` method MUST accept `(state, config)` and return a state update dict

#### Scenario: Node with no dependencies

- **WHEN** a node (e.g., unhandled response) requires no external dependencies
- **THEN** it MUST still be implemented as a class conforming to the `(state, config) -> dict` contract

#### Scenario: LangGraph invokes node with config

- **WHEN** the compiled graph executes a node
- **THEN** it SHALL invoke the node's `__call__` method with both the current state and the runnable config

### Requirement: Pipeline-Stage Sub-Package Layout

Graph nodes SHALL be organized into sub-packages under `src/muggle/core/` grouped by pipeline stage:

| Stage    | Sub-package | Nodes                    |
|----------|-------------|--------------------------|
| Guard    | `guard/`    | intent_check, unhandled  |
| Memory   | `memory/`   | summarize                |
| Search   | `search/`   | query_rewrite, retrieval |
| Response | `response/` | inquiry                  |

Each sub-package MUST be a valid Python package containing an `__init__.py` and MAY export its node class(es).

#### Scenario: Importing a node from its stage package

- **WHEN** `GraphProcessor` needs the intent check node
- **THEN** it SHALL import it as `from muggle.core.guard import IntentCheckNode`

### Requirement: Dependency Injection at Construction

`GraphProcessor.__init__` SHALL be the composition root that reads configuration and injects dependencies into node constructors. Nodes MUST NOT read global configuration (`cfg`) directly.

#### Scenario: GraphProcessor wires retrieval node

- **WHEN** `GraphProcessor` is initialized
- **THEN** it SHALL read rerank parameters from `cfg`
- **AND** it SHALL pass `recall_limit` and `relevance_threshold` as scalar arguments to `RetrievalNode.__init__`

#### Scenario: Node is testable without global config

- **WHEN** a node is instantiated in a test
- **THEN** all its dependencies SHALL be injectable via its constructor without requiring `cfg` to be available

### Requirement: Structured Output Models Belong to Nodes

Pydantic models used for `with_structured_output` SHALL be defined in the same module as the node that uses them.

#### Scenario: IntentCheckResult defined with IntentCheckNode

- **WHEN** `IntentCheckNode` invokes the LLM with structured output
- **THEN** the `IntentCheckResult` model SHALL be defined in `guard/intent_check.py`

### Requirement: Third-Party Runnable Nodes Used Directly

Nodes implemented by external libraries as standard `Runnable` objects SHALL be registered directly in the graph assembly without wrapper classes.

#### Scenario: SummarizationNode registered directly

- **WHEN** `GraphProcessor` builds the graph
- **THEN** langmem's `SummarizationNode` SHALL be instantiated and passed directly to `builder.add_node()` without an adapter class
