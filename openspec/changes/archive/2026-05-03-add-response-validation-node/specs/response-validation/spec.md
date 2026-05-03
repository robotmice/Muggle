# Capability: response-validation

## Purpose

Defines the validation gate that scores InquiryNode output against quality criteria and implements automatic retry with loopback on failure.

## ADDED Requirements

### Requirement: Inquiry Response Validation

The system SHALL validate every InquiryNode response using LLM-based structured output against the `prompt-validate` quality rubric before delivering it to the user.

#### Scenario: Validation passes

- **WHEN** the ValidateNode evaluates an Inquiry response
- **AND** the LLM returns `decision: true` (score ≥ configured threshold)
- **THEN** the graph SHALL route to END with the response unchanged

#### Scenario: Validation fails with retries remaining

- **WHEN** the ValidateNode evaluates an Inquiry response
- **AND** the LLM returns `decision: false`
- **AND** `retry_count` is less than 5
- **THEN** the graph SHALL route back to the Summarization node for re-generation
- **AND** `retry_count` SHALL be incremented by 1

#### Scenario: Validation fails with exhausted retries

- **WHEN** the ValidateNode evaluates an Inquiry response
- **AND** the LLM returns `decision: false`
- **AND** `retry_count` is 5 or greater
- **THEN** the graph SHALL route to the UnhandledNode

### Requirement: Validation Node Contract

The ValidateNode SHALL follow the standard node contract: a class receiving dependencies via `__init__` and returning a `dict` of state field updates from `__call__(self, state, config)`.

#### Scenario: ValidateNode construction

- **WHEN** `GraphProcessor` initializes the ValidateNode
- **THEN** it SHALL inject the LLM model, PromptRegistry, and a threshold value via the constructor
- **AND** the threshold SHALL be read from `cfg.get_validate_params()`

#### Scenario: ValidateNode structured output

- **WHEN** the ValidateNode invokes the LLM
- **THEN** it SHALL use `with_structured_output` with a Pydantic model containing at minimum `decision: bool`
- **AND** the Pydantic model SHALL be defined in the same module as the node

### Requirement: Retry Counter Lifecycle

The system SHALL track retry attempts via a `retry_count` field on `WorkflowState` that resets to 0 for each new user message.

#### Scenario: Counter increments on failure

- **WHEN** validation fails
- **THEN** `retry_count` SHALL be incremented by 1

#### Scenario: Counter resets on new message

- **WHEN** a new user message passes through IntentCheckNode
- **THEN** `retry_count` SHALL be reset to 0

#### Scenario: Counter unchanged on validation pass

- **WHEN** validation passes
- **THEN** `retry_count` SHALL remain unchanged

### Requirement: Configurable Validation Threshold

The validation decision threshold SHALL be configurable via `config.toml` under a `[validate]` section with a `threshold` key.

#### Scenario: Threshold from config

- **WHEN** `cfg.get_validate_params()` is called
- **THEN** it SHALL return a dict containing at least `{"threshold": <float>}`
- **AND** the default value SHALL be 0.8 if not specified in config
