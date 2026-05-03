## Context

`GraphProcessor.__init__` currently creates all node implementations as closures, parses multiple config sections, instantiates `DashScopeRerank` and `SummarizationNode`, builds the `StateGraph`, and compiles the workflow — all in one ~150-line method. Four of six node implementations are closures; the other two (`unhandled_response_node`, `ingest_router`) are module-level functions. This is a recognized pain point and the primary motivation for this refactor.

The existing specs (`llm-processor`, `structure`) define behavioral requirements and package conventions. No behavior changes are in scope — the graph topology, node responsibilities, and external API surface remain identical.

## Goals / Non-Goals

**Goals:**
- Extract each node into a standalone, testable class under a purpose-named sub-package
- Define a consistent node contract: `__call__(self, state: WorkflowState, config: RunnableConfig) -> dict`
- Shrink `GraphProcessor.__init__` to a declarative composition root (~30 lines)
- Keep `ProcessorInterface`, the constructor signature, and `get_response` behavior unchanged

**Non-Goals:**
- Changing graph topology or node responsibilities
- Wrapping `SummarizationNode` in an adapter class
- Creating a `GraphBuilder` abstraction over `StateGraph`
- Modifying existing specs (behavior is preserved)

## Decisions

### D1: Grouped by pipeline concern (Option B)

Each pipeline stage gets its own sub-package:

```
src/muggle/core/
├── guard/        # intent_check, unhandled
├── memory/       # summarize (SummarizationNode)
├── search/       # query_rewrite, retrieval
└── response/     # inquiry
```

Alternative considered: Flat `nodes/` directory with one file per node class. Rejected because grouping by stage makes the pipeline's structure visible in the filesystem and keeps related nodes co-located (e.g., query_rewrite and retrieval are both "finding information").

### D2: Node contract includes `config`

Every node class follows:

```python
class SomeNode:
    def __init__(self, ...dependencies...):
        ...

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        ...
```

LangGraph natively invokes nodes as `node(state, config)`. Accepting `config` enables future nodes to access `configurable` fields (e.g., `thread_id`), and makes the contract forward-compatible. The param is optional with a default for nodes that don't need it.

### D3: SummarizationNode used raw

langmem's `SummarizationNode` is already a `Runnable` with a compatible signature. It gets registered directly in the graph assembly:

```python
SummarizationNode(
    model=model,
    max_tokens=...,
    max_tokens_before_summary=...,
    max_summary_tokens=...,
    input_messages_key="messages",
    output_messages_key="messages",
)
```

Alternative considered: Wrapping in an adapter class. Rejected — adds indirection without benefit. The node already conforms to langgraph's invocation protocol.

### D4: No `GraphBuilder` wrapper

`StateGraph` already has a clean declarative API (`add_node`, `add_edge`, `add_conditional_edges`, `compile`). A wrapper would be a thin pass-through that adds complexity without value. Graph assembly stays in `GraphProcessor.__init__` — just with nodes injected by constructor, not defined as closures.

### D5: Result models live with their nodes

`IntentCheckResult`, `InquiryResult`, `QueryRewriteResult` move from `graph_processor.py` to their respective node modules. These pydantic models are implementation details of how a specific node calls `with_structured_output` — they don't need to be shared.

### D6: Dependency injection at construction

Config values are threaded through node constructors from `GraphProcessor.__init__`, not read from `cfg` inside nodes. This keeps nodes decoupled from global config and makes them testable with fakes.

```
GraphProcessor.__init__
    reads cfg  →  injects into constructor
    reads cfg  →  injects into constructor
    ...
    assembles graph
```

## Risks / Trade-offs

- **More files** (8 new modules) → Low risk. Clear naming and grouping avoids discoverability issues.
- **No behavior changes** → Tests should pass without modification. If they don't, something was wired wrong.
- **`thread_id` in `config_map`** → The current `config_map(thread_id)` helper is used in `get_response`. It stays in `state.py`; the new `config` param on nodes doesn't change how the graph is invoked from outside.
