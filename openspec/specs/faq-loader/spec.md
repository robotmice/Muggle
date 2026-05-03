# Capability: faq-loader

## Purpose
Provides functionality for parsing markdown FAQ files and ingesting them into the vector store with multi-level embedding strategies.

## Requirements

### Requirement: FAQ Markdown Ingestion with Dual Embeddings
The system SHALL provide a program to parse the `aia_faq.md` file and ingest sections into Milvus. For each section, the program MUST generate two embeddings:
1. One for the section heading (H3).
2. One for the combined heading and section body (or chunked segment).

#### Scenario: Successful ingestion with dual embeddings
- **WHEN** the loading program is executed with `aia_faq.md`
- **THEN** it correctly identifies H3 headers and their associated bodies, generates both required embeddings, and stores them in Milvus records.

### Requirement: Multi-Level FAQ Ingestion (Sections and Segments)
For every FAQ section identified (H3 + body), the system MUST store the full section as a record. Additionally, if the section exceeds 200 characters, it MUST also store chunked segments.

#### Scenario: Ingesting a small section
- **WHEN** a section (Heading + Body) is <= 200 characters
- **THEN** the system stores one record containing the full section.

#### Scenario: Ingesting a large section with segments
- **WHEN** a section (Heading + Body) exceeds 200 characters
- **THEN** the system stores one record containing the full section (H3 + full body).
- **AND** it splits the body using `RecursiveCharacterTextSplitter` (with a 20-character overlap).
- **AND** it prepends the H3 heading to each resulting segment.
- **AND** each "Heading + Segment" pair is stored as an *additional* distinct record in Milvus.

### Requirement: Idempotent Loading
The loading program SHOULD handle duplicate ingestion gracefully, ensuring that the same content is not added multiple times or is updated correctly.

#### Scenario: Re-running the loader
- **WHEN** the loading program is run a second time with the same input file
- **THEN** it detects existing entries and either skips them or updates them without creating duplicates.
