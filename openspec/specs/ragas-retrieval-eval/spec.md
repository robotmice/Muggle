# Capability: ragas-retrieval-eval

## Purpose

LLM-as-judge retrieval quality evaluation using Ragas metrics (Context Precision, Context Recall, Context Relevance, Context Entity Recall), replacing the need for human-labeled `relevant_ids` with natural-language `reference` answers.

## Requirements

### Requirement: Script entry point and CLI

The system SHALL provide `eval_retrieval_ragas.py` as a standalone evaluation script at the project root with the same CLI interface as `eval_retrieval.py`.

#### Scenario: Run with default arguments

- **WHEN** the user executes `poetry run python eval_retrieval_ragas.py`
- **THEN** the script loads `sample_test_queries.json`, connects to Milvus, evaluates three retrieval configs, and prints a report to stdout

#### Scenario: Specify dataset file

- **WHEN** the user executes `poetry run python eval_retrieval_ragas.py --dataset my_queries.json`
- **THEN** the script loads `my_queries.json` as the test dataset

#### Scenario: Export CSV report

- **WHEN** the user executes `poetry run python eval_retrieval_ragas.py --output report.csv`
- **THEN** the script writes evaluation results to `report.csv` in CSV format

#### Scenario: Generate sample dataset

- **WHEN** the user executes `poetry run python eval_retrieval_ragas.py --generate-sample`
- **THEN** the script creates a sample dataset file with `query`, `reference`, and `lang_tag` fields and exits

#### Scenario: Specify default language

- **WHEN** the user executes `poetry run python eval_retrieval_ragas.py --lang zh-CN`
- **THEN** queries without an explicit `lang_tag` field default to `zh-CN`

### Requirement: Dataset loading and validation

The system SHALL load a JSON dataset where each item contains a `query` field (required) and optionally `reference` and `lang_tag`.

#### Scenario: Valid dataset

- **WHEN** the dataset file contains an array of objects each with a `query` field
- **THEN** the script loads all items successfully

#### Scenario: Missing query field

- **WHEN** any item in the dataset lacks a `query` field
- **THEN** the script raises a ValueError and exits with a clear message identifying the invalid item

#### Scenario: Missing reference field

- **WHEN** a query item lacks a `reference` field
- **THEN** the script skips that query for metrics requiring reference and logs a warning

### Requirement: Ragas metric computation

The system SHALL compute Context Precision, Context Recall, Context Relevance, and Context Entity Recall using Ragas with the project's configured LLM for each of the three retrieval configurations.

#### Scenario: Metric computation per query

- **WHEN** a query has both `query` and `reference` fields
- **THEN** the script builds a `SingleTurnSample` with the query as `user_input`, retrieved document texts as `retrieved_contexts`, and `reference`, and computes all four metrics

#### Scenario: Query without reference

- **WHEN** a query lacks a `reference` field
- **THEN** only Context Relevance (which does not require reference) is computed for that query

#### Scenario: LLM failure during metric computation

- **WHEN** an LLM API call fails for a specific metric on a specific sample
- **THEN** the script records the failure, reports `NaN` for that metric-query pair, and continues evaluating remaining metrics and queries

### Requirement: Evaluation across retrieval configurations

The system SHALL evaluate and compare three retrieval configurations: vector-only (dense ANN only), hybrid (dense + sparse BM25 with RRF fusion), and hybrid+rerank (hybrid retrieval with DashScope rerank and relevance threshold filtering).

#### Scenario: Three-config comparison

- **WHEN** the script runs evaluation
- **THEN** it evaluates and reports metrics for vector-only, hybrid, and hybrid+rerank configurations side by side

#### Scenario: Config uses appropriate search method

- **WHEN** retrieval mode is `vector_only`
- **THEN** the RetrievalNode uses `VectorStoreManager.search()` (dense-only)

#### Scenario: Hybrid config uses RRF fusion

- **WHEN** retrieval mode is `hybrid`
- **THEN** the RetrievalNode uses `VectorStoreManager.hybrid_search()` (dense + sparse with RRF)

### Requirement: Report output

The system SHALL print a formatted terminal report and optionally export results to CSV.

#### Scenario: Terminal report

- **WHEN** evaluation completes
- **THEN** the script prints a table with one row per config containing average Context Precision, Context Recall, Context Relevance, Context Entity Recall, and number of retrieved documents

#### Scenario: CSV export

- **WHEN** the `--output` flag is provided with a file path
- **THEN** the script writes a CSV file with config names and all metric columns

#### Scenario: Best config highlights

- **WHEN** the terminal report is printed
- **THEN** the script identifies and prints the best config for Context Precision and Context Recall
