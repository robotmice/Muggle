## Context

`eval_retrieval.py` evaluates retrieval quality using rank-based metrics (P@k, R@k, nDCG, MRR) that require human-labeled `relevant_ids`. This doesn't scale beyond small test sets. Ragas (already a dev dependency) offers LLM-as-judge metrics that evaluate semantic relevance — whether retrieved chunks actually help answer the question — using a natural-language `reference` answer per query instead of doc IDs.

The new script `eval_retrieval_ragas.py` runs the same three retrieval configs (vector-only, hybrid, hybrid+rerank) through the same `RetrievalNode` but scores them with Ragas metrics powered by the project's existing DeepSeek LLM.

## Goals / Non-Goals

**Goals:**
- Evaluate retrieval quality without requiring human-labeled `relevant_ids`
- Use four Ragas metrics: Context Precision, Context Recall, Context Relevance, Context Entity Recall
- Same CLI interface and workflow as `eval_retrieval.py`
- Reuse existing `RetrievalNode`, `VectorStoreManager`, and config infra

**Non-Goals:**
- Evaluating generation quality (Faithfulness, Answer Correctness, etc.) — retrieval only
- Modifying or removing `eval_retrieval.py`
- Synthetic test set generation
- Changing the retrieval pipeline itself

## Decisions

### D1: Metrics selection — four Context metrics

We use `ContextPrecision`, `ContextRecall`, `ContextRelevance`, and `ContextEntityRecall` from `ragas.metrics.collections`.

| Metric | What it measures | Needs LLM? | Needs reference? |
|---|---|---|---|
| Context Precision | Are retrieved chunks relevant to the reference? | Yes | Yes |
| Context Recall | Does the retrieved set cover everything in the reference? | Yes | Yes |
| Context Relevance | What fraction of retrieved content is actually relevant? | Yes | No |
| Context Entity Recall | How many key entities from reference appear in retrieved text? | No | Yes |

**Alternative considered**: Including generation metrics (Faithfulness, Answer Relevancy). Rejected because it conflates retrieval quality with generation quality and requires running the full graph through the Inquiry node — a different eval concern.

### D2: LLM initialization — standalone ModelRegistry instance

The script creates its own `ModelRegistry` instance and registers the default model using `cfg.get_llm_params()`, mirroring `app.py`. This avoids depending on the Flask app context.

```python
registry = ModelRegistry()
params = cfg.get_llm_params()
registry.register("llm-default", params["provider"], params["model"],
                   temperature=params["temperature"])
llm = registry.get_model("llm-default")
```

**Alternative considered**: Using `init_chat_model` directly. Rejected because ModelRegistry is the project convention and makes it easy to swap models via config.

### D3: Dataset format — `reference` text field replaces `relevant_ids`

```json
{
  "query": "How to file an insurance claim?",
  "reference": "Claims can be filed online, by phone, or via mail within 30 days.",
  "lang_tag": "en-US"
}
```

`lang_tag` is optional (defaults to `en-US`, same as current script). `reference` is required for three of four metrics; queries without `reference` are skipped with a warning.

**Alternative considered**: Adding `reference` alongside `relevant_ids` for backward compatibility. Rejected since the goal is a clean Path B — full Ragas replacement, not a hybrid.

### D4: Script structure — mirrors eval_retrieval.py pattern

Same flow: load dataset → init vector stores → for each config: build node → evaluate → collect metrics → print report → optionally export CSV.

Differences:
- `evaluate_config` builds `SingleTurnSample` objects per query instead of running `precision_at_k`/`recall_at_k`/etc.
- Metrics are computed via `metric.single_turn_score(sample)` per query, then averaged.
- A `RagasMetrics` dataclass groups the four metric instances, initialized once with the LLM.

### D5: Error handling for LLM failures

Individual metric failures (network errors, rate limits) are caught per-sample and reported as `NaN` in the aggregate. The script continues computing other metrics and queries. A summary of failures is printed at the end.

## Risks / Trade-offs

- **LLM cost**: Each metric that requires LLM makes API calls per query per config. For 10 queries × 3 configs × 2 LLM metrics, that's ~60 LLM calls. Mitigation: print a cost estimate before running and allow the user to Ctrl-C.
- **LLM judge accuracy**: The DeepSeek model evaluating relevance may disagree with human judgment. Context Entity Recall (lexical, no LLM) provides a grounding baseline.
- **Reference quality**: Metrics are only as good as the reference text. Vague references produce noisy scores. Mitigation: the `--generate-sample` flag produces a template with a `reference` field and usage notes.
