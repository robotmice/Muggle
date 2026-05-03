## ADDED Requirements

### Requirement: Internal Cleanup
This change is an internal refactoring and does not introduce or modify any spec-level requirements.

#### Scenario: Validation remains consistent
- **WHEN** the processor is warmed up with a missing model
- **THEN** it SHALL still raise a ValueError as it did before, but delegated to the registry.
