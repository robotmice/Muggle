# Capability: law-loader

## Purpose
Parses the Social Insurance Law of the PRC markdown document (chapters + articles) and ingests articles into a dedicated Milvus collection with dual-vector embeddings and BM25 sparse vectors.

## Requirements

### Requirement: Law Markdown Ingestion with Dual Embeddings

The system SHALL provide a program to parse the Social Insurance Law markdown file and ingest articles into a dedicated Milvus collection. For each article, the program MUST generate two embeddings:
1. One for the article heading prefixed with the chapter name (e.g., "工伤保险 — 第三十六条").
2. One for the combined heading and article body (or chunked segment).

#### Scenario: Successful ingestion with dual embeddings

- **WHEN** the loading program is executed with `中华人民共和国社会保险法.md`
- **THEN** it correctly identifies `##` chapter headers and `**第X条**` articles within each chapter
- **AND** generates `header_vector` from the chapter-prefixed article heading
- **AND** generates `content_vector` from the combined heading and body
- **AND** stores both vectors in the law collection with `lang_tag = "zh-CN"`

### Requirement: Multi-Level Law Ingestion (Articles and Segments)

For every article identified, the system MUST store the full article as a record. Additionally, if the article exceeds 200 characters, it MUST also store chunked segments.

#### Scenario: Ingesting a short article

- **WHEN** an article (heading + body) is <= 200 characters
- **THEN** the system stores one record containing the full article

#### Scenario: Ingesting a long article with segments

- **WHEN** an article (heading + body) exceeds 200 characters
- **THEN** the system stores one record containing the full article
- **AND** it splits the body using `RecursiveCharacterTextSplitter` (chunk_size=300, chunk_overlap=20)
- **AND** it prepends the chapter-prefixed heading to each resulting segment
- **AND** each "heading + segment" pair is stored as an additional distinct record with `is_segment=True`

### Requirement: Idempotent Law Loading

The loading program SHALL handle duplicate ingestion gracefully using MD5-based deterministic IDs for upsert.

#### Scenario: Re-running the law loader

- **WHEN** the loading program is run a second time with the same input file
- **THEN** it upserts records by their deterministic IDs without creating duplicates

### Requirement: Chapter-Article Structure Parsing

The loader SHALL split the document by chapter (`##`), then by article (`**第X条**` with Chinese numerals), and SHALL skip non-content sections.

#### Scenario: Parsing the law document

- **WHEN** the loader processes the Social Insurance Law markdown
- **THEN** it skips the table of contents (目录) section
- **AND** it skips the source attribution line at the bottom of the document
- **AND** it associates each article with its parent chapter name
- **AND** the article header is formatted as `"{chapter_name} — {article_number}"`
