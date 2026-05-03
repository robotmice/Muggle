## 1. State and Config

- [x] 1.1 Add `retry_count` (int, default 0) and `pass_validation` (bool, default False) fields to `WorkflowState` in `state.py`
- [x] 1.2 Add `validation_router(state: WorkflowState) -> str` function to `state.py` routing on `pass_validation` and `retry_count`
- [x] 1.3 Add `get_validate_params()` method to `ConfigManager` in `config.py` returning `{"threshold": float}` with default 0.8
- [x] 1.4 Add `[validate]` section with `threshold = 0.8` to `config.toml`

## 2. ValidateNode

- [x] 2.1 Create `src/muggle/core/validate.py` with `ValidationResult` Pydantic model (decision: bool, score: float, critical_flaws: list[str])
- [x] 2.2 Implement `ValidateNode` class conforming to standard node contract (model + prompt_registry + threshold in `__init__`, dict from `__call__`)
- [x] 2.3 ValidateNode returns `pass_validation` and `retry_count` (incremented on failure) in its state update dict

## 3. Graph Wiring

- [x] 3.1 In `graph_processor.py`, import `ValidateNode` from `core/validate` and `validation_router` from `state`
- [x] 3.2 Read validate params via `cfg.get_validate_params()` and instantiate `ValidateNode`
- [x] 3.3 Add ValidateNode to graph builder as `STR_NODE_VALIDATE`
- [x] 3.4 Replace `Inquiry → END` edge with `Inquiry → Validate`
- [x] 3.5 Add conditional edges from Validate using `validation_router` mapping to END, STR_NODE_UNHANDLED, and STR_NODE_SUMMARIZE

## 4. Counter Reset

- [x] 4.1 Add `"retry_count": 0` to `IntentCheckNode.__call__` return dict in `guard/intent_check.py`

## 5. Tests

- [x] 5.1 Add test for ValidateNode passing a valid response
- [x] 5.2 Add test for ValidateNode failing and incrementing retry_count
- [x] 5.3 Add test for validation router routing to END on pass
- [x] 5.4 Add test for validation router routing to Unhandled when retry_count >= 5
- [x] 5.5 Add test for validation router routing to Summarization on fail with retries remaining
- [x] 5.6 Add test for IntentCheckNode resetting retry_count to 0
- [x] 5.7 Run full test suite to verify no regressions
