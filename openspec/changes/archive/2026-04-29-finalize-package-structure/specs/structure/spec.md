# Spec: structure (Delta)

## Requirements

### Requirement: Explicit Package Markers
Every directory within the `src/muggle/` hierarchy that contains source code or resources MUST be an explicit Python package.

#### Scenario: Package Discovery
- **GIVEN** a directory in the `src/muggle/` source tree
- **THEN** it MUST contain an `__init__.py` file (even if empty).

#### Scenario: Sub-package Discovery
- **GIVEN** the `prompts` resource directory
- **THEN** both `prompts/system` and `prompts/user` MUST contain `__init__.py` files to be correctly identified as sub-packages for resource loading.
