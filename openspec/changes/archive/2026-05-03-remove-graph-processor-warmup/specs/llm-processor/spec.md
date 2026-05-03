## REMOVED Requirements

### Requirement: Robust Processor Initialization
**Reason**: The warm-up validation (`warm_up()` calling `registry.get_model()`) is the only consumer of this requirement. With warm-up removed, `GraphProcessor.__init__` already constructs all nodes (which will fail fast if the model registry is misconfigured).

**Migration**: No migration needed. The `GraphProcessor` constructor naturally fails on misconfiguration — `ModelRegistry.get_model()` raises `ValueError` for unregistered aliases and `init_chat_model` raises on unreachable providers.
