## Why

`eval_retrieval.py` requires human-labeled `relevant_ids` per query to compute P@k/R@k/nDCG — this doesn't scale. We already depend on Ragas (v0.4.3, dev), which offers LLM-as-judge metrics (Context Precision, Context Recall, Context Relevancy, Context Entity Recall) that only need a natural-language `reference` answer per query. Replacing label-driven eval with Ragas removes the labeling bottleneck while evaluating semantic relevance instead of ID-matching.

## What Changes

- New script `eval_retrieval_ragas.py` that replaces rank-based metrics (P@k, R@k, nDCG, MRR) with Ragas metrics
- Dataset format shifts from `relevant_ids` (Milvus doc IDs) to `reference` (ground truth answer text)
- Same three-config comparison: vector-only, hybrid, hybrid+rerank
- Same CLI interface: `--dataset`, `--output`, `--generate-sample`, `--lang`
- Uses the project's existing LLM config for Ragas metric computation
- Existing `eval_retrieval.py` is left untouched

## Capabilities

### New Capabilities

- `ragas-retrieval-eval`: LLM-as-judge retrieval quality evaluation using Ragas Context Precision, Context Recall, Context Relevancy, and Context Entity Recall

### Modified Capabilities

None — this is a standalone addition that uses existing retrieval infra without changing its behavior.

## Impact

- **New file**: `eval_retrieval_ragas.py` (project root)
- **New test file**: `tests/test_eval_retrieval_ragas.py`
- **Dependencies**: `ragas` (already in dev deps), `langchain` (already in deps)
- **No changes** to `eval_retrieval.py`, core graph nodes, or existing specs
