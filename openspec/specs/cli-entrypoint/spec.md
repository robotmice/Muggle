# Capability: CLI Entrypoint

## Purpose
The CLI Entrypoint capability enables the application to be easily executed via the command line using standard Poetry commands, providing a consistent and user-friendly way to start the Flask development server.

## Requirements

### Requirement: Execution via Poetry script
The system MUST allow execution using the `muggle` command when installed or managed via Poetry.

#### Scenario: Running the application command
- **WHEN** the user executes `poetry run muggle` in the terminal
- **THEN** the Flask development server starts on port 5000

### Requirement: Encapsulated run function
The `muggle.app` module MUST provide a `run` function that serves as the entry point for the application.

#### Scenario: Calling the run function directly
- **WHEN** the `run()` function in `src/muggle/app.py` is invoked
- **THEN** the Flask application starts running with the configured settings
