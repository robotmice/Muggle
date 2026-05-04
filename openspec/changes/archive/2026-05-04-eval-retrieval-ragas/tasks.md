## 1. Script skeleton

- [x] 1.1 Create `eval_retrieval_ragas.py` at project root with argparse CLI mirroring `eval_retrieval.py` (--dataset, --lang, --output, --generate-sample)
- [x] 1.2 Implement `generate_sample_dataset()` that writes `query` + `reference` + `lang_tag` template JSON
- [x] 1.3 Implement `load_dataset()` that validates `query` field presence and applies `lang_tag` defaults

## 2. LLM and metric setup

- [x] 2.1 Implement `init_ragas_llm()` that creates a ModelRegistry, registers the default LLM from config, and returns the langchain model instance
- [x] 2.2 Implement `build_metrics(llm)` that constructs and returns the four Ragas metric instances (ContextPrecision, ContextRecall, ContextRelevance, ContextEntityRecall) in a dataclass or dict

## 3. Core evaluation logic

- [x] 3.1 Implement `build_node()` — same as `eval_retrieval.py`'s version, reusing RetrievalNode construction with the three config variants
- [x] 3.2 Implement `run_retrieval()` that calls a RetrievalNode with a query + lang_tag and returns retrieved document texts
- [x] 3.3 Implement `evaluate_config()` that iterates the dataset, builds SingleTurnSample per query, computes all four metrics, handles LLM failures gracefully (NaN on error), and returns averaged metrics

## 4. Report output

- [x] 4.1 Implement `print_report()` that prints a formatted terminal table with one row per config and metric columns
- [x] 4.2 Implement `export_csv()` that writes results to a CSV file

## 5. Tests

- [x] 5.1 Create `tests/test_eval_retrieval_ragas.py` with mocked Ragas metrics, mocked RetrievalNode, and mocked Milvus — test dataset loading, metric aggregation, report formatting, and the NaN-on-failure path
