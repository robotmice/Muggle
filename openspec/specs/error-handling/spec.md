# Capability: error-handling

## Purpose
TBD - Defines the standard error handling patterns and custom exceptions for the application.

## Requirements

### Requirement: Domain-Specific Exceptions
The system MUST provide a set of custom exceptions that inherit from a base `MuggleError`.

#### Scenario: Raising a custom exception
- **WHEN** a prompt is not found
- **THEN** the system MUST raise a `PromptNotFoundError` exception.

### Requirement: Granular Error Reporting
Custom exceptions MUST include descriptive error messages that specify the failed operation and relevant context (e.g., prompt name and type).

#### Scenario: Error message content
- **WHEN** `PromptNotFoundError` is raised for a prompt named "missing" of type "system"
- **THEN** the exception message MUST contain both the name "missing" and the type "system".
