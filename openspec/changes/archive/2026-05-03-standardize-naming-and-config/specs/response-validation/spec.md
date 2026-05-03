## MODIFIED Requirements

### Requirement: Inquiry Response Validation

The system SHALL validate every InquiryNode response using LLM-based structured output against the `prompt-validation` quality rubric before delivering it to the user.

#### Scenario: Validation passes

- **WHEN** the ValidationNode evaluates an Inquiry response
- **AND** the LLM returns `decision: true` (score >= configured threshold)
- **THEN** the graph SHALL route to END with the response unchanged

#### Scenario: Validation fails with attempts remaining

- **WHEN** the ValidationNode evaluates an Inquiry response
- **AND** the LLM returns `decision: false`
- **AND** `attempt_count` is less than the configured `max_attempts`
- **THEN** the graph SHALL route back to the Summarization node for re-generation
- **AND** `attempt_count` SHALL be incremented by 1

#### Scenario: Validation fails with exhausted attempts

- **WHEN** the ValidationNode evaluates an Inquiry response
- **AND** the LLM returns `decision: false`
- **AND** `attempt_count` is greater than or equal to `max_attempts`
- **THEN** the graph SHALL route to the FallbackNode

### Requirement: Validation Node Contract

The ValidationNode SHALL follow the standard node contract: a class receiving dependencies via `__init__` and returning a `dict` of state field updates from `__call__(self, state, config)`.

#### Scenario: ValidationNode construction

- **WHEN** `GraphProcessor` initializes the ValidationNode
- **THEN** it SHALL inject the LLM model, PromptRegistry, and a threshold value via the constructor
- **AND** the threshold SHALL be read from `cfg.get_validate_params()`

#### Scenario: ValidationNode structured output

- **WHEN** the ValidationNode invokes the LLM
- **THEN** it SHALL use `with_structured_output` with a Pydantic model containing at minimum `decision: bool`
- **AND** the Pydantic model SHALL be defined in the same module as the node

### Requirement: Attempt Counter Lifecycle

The system SHALL track validation attempts via an `attempt_count` field on `WorkflowState` that resets to 0 for each new user message.

#### Scenario: Counter increments on failure

- **WHEN** validation fails
- **THEN** `attempt_count` SHALL be incremented by 1

#### Scenario: Counter resets on new message

- **WHEN** a new user message passes through IntentCheckNode
- **THEN** `attempt_count` SHALL be reset to 0

#### Scenario: Counter unchanged on validation pass

- **WHEN** validation passes
- **THEN** `attempt_count` SHALL remain unchanged

### Requirement: Configurable Validation Threshold and Max Attempts

The validation decision threshold and maximum attempts SHALL be configurable via `config.toml` under a `[validate]` section with `threshold` and `max_attempts` keys. The validation router SHALL be a `ValidationRouter` class that receives `max_attempts` at construction.

#### Scenario: Threshold and max attempts from config

- **WHEN** `cfg.get_validate_params()` is called
- **THEN** it SHALL return a dict containing at least `{"threshold": <float>, "max_attempts": <int>}`
- **AND** the default value for `threshold` SHALL be 0.8 if not specified in config
- **AND** the default value for `max_attempts` SHALL be 5 if not specified in config

#### Scenario: ValidationRouter routes with configurable max

- **WHEN** `ValidationRouter(max_attempts=3)` is called with a state where `attempt_count=3` and `pass_validation=False`
- **THEN** it SHALL route to the FallbackNode
