## Why

The `warm_up` method in `ChatProcessor` currently performs a manual check for model registration (`is_registered`) and raises a `ValueError` if the model is missing. However, the `ModelRegistry.get_model()` method already performs this exact check and raises a similar exception. This redundancy is unnecessary and makes the implementation less clean.

## What Changes

- Remove the redundant `is_registered` check from `ChatProcessor.warm_up` in `src/muggle/core/graph_processor.py`.
- Remove the manual `ValueError` raise, letting `self.registry.get_model` handle the validation.

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- **Affected Files**: `src/muggle/core/graph_processor.py`
- **Internal Behavior**: No functional change; error reporting for missing models remains consistent but is delegated to the registry.