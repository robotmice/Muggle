## MODIFIED Requirements

### Requirement: Health Monitoring
The application SHALL expose a GET endpoint at `/health` to report the status of the internal application state. This endpoint MUST be defined within a dedicated `monitoring` blueprint.

#### Scenario: Healthy state
- **WHEN** a GET request is received at `/health` AND the processor is present in the application context
- **THEN** the system returns a 200 OK status with `{ "status": "healthy" }`

#### Scenario: Unhealthy state
- **WHEN** a GET request is received at `/health` AND the processor is not present in the application context
- **THEN** the system returns a 503 Service Unavailable status with `{ "status": "unhealthy", "errors": [...] }`

## REMOVED Requirements

### Requirement: Graceful Warm-up
**Reason**: The warm-up probe catches LLM connectivity issues at startup but the server continues running either way (exception is caught and logged). Failing at first request is equivalent behavior with less machinery.

**Migration**: Remove the `try: processor.warm_up() except: log` block from `app.py`. No action needed for callers — the first `/chat` request surfaces LLM connectivity issues directly.
