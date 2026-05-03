## Why

`GraphProcessor.__init__` is a 150-line monolith where node implementations, config parsing, dependency wiring, and graph assembly are all crammed into one method via closures. This makes nodes untestable in isolation, obscures dependency boundaries, and forces every change to touch the same file.

## What Changes

- Extract each graph node into its own class under purpose-named sub-packages (`guard/`, `memory/`, `search/`, `response/`)
- New node contract: `__call__(self, state: WorkflowState, config: RunnableConfig) -> dict`
- `GraphProcessor` becomes a thin composition root — injects dependencies, assembles the graph, delegates to `self.workflow`
- Move `WorkflowState`, router functions, and config helpers from `graph_processor.py` + module-level helpers into a dedicated `state.py`
- Move structured-output result models (`IntentCheckResult`, `InquiryResult`, `QueryRewriteResult`) into their respective node modules
- `SummarizationNode` (langmem) used raw — registered directly in graph assembly, no wrapper

## Capabilities

### New Capabilities

- `graph-node-architecture`: Standard node contract, per-stage sub-package layout, dependency injection at construction, and graph assembly patterns for LangGraph nodes

### Modified Capabilities

None — this is a pure refactor. All existing behavioral requirements in `llm-processor` remain unchanged.

## Impact

- `src/muggle/core/` — new sub-packages (`guard/`, `memory/`, `search/`, `response/`) and extracted `state.py`
- `src/muggle/core/graph_processor.py` — major rewrite (shrink from ~220 to ~80 lines)
- `src/muggle/blueprints/chat.py` — no change (consumes `ProcessorInterface`, not implementation details)
- `src/muggle/app.py` — no change (same constructor signature)
