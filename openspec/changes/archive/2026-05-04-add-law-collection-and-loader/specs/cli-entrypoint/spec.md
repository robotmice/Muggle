## ADDED Requirements

### Requirement: Law loader CLI entry point

The system MUST provide a `load-law` command accessible via `poetry run load-law` for ingesting the Social Insurance Law markdown into Milvus.

#### Scenario: Running the law loader command

- **WHEN** the user executes `poetry run load-law --file 中华人民共和国社会保险法.md`
- **THEN** the law loader parses the file and upserts articles into the law collection

#### Scenario: Default file and language

- **WHEN** the user executes `poetry run load-law` with no arguments
- **THEN** it defaults to `中华人民共和国社会保险法.md` for the file and `zh-CN` for the language tag
