#!/usr/bin/env python3
"""Retrieval quality evaluation using Ragas LLM-as-judge metrics.

Compares three configurations:
  1. vector-only  — dense ANN search only
  2. hybrid        — dense + sparse (BM25) with RRF fusion, no rerank
  3. hybrid+rerank — hybrid retrieval + DashScope rerank + relevance threshold

Metrics (Ragas):
  - Context Precision   — are retrieved chunks relevant to the reference? (LLM)
  - Context Recall      — does the retrieved set cover the reference? (LLM)
  - Context Relevance   — what fraction of retrieved content is relevant? (LLM, no reference needed)
  - Context Entity Recall — do key entities from reference appear in retrieved text? (lexical)

Usage:
  poetry run python eval_retrieval_ragas.py
  poetry run python eval_retrieval_ragas.py --dataset sample_test_queries.json
  poetry run python eval_retrieval_ragas.py --output report.csv
"""

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank
from ragas import SingleTurnSample
from ragas.metrics.collections import (
    ContextEntityRecall,
    ContextPrecision,
    ContextRecall,
    ContextRelevance,
)

from muggle.core.search.retrieval import RetrievalNode
from muggle.core.state import WorkflowState
from muggle.infra.config import cfg
from muggle.infra.registry import ModelRegistry, VectorStoreManager

SAMPLE_DATASET = "sample_test_queries.json"

METRIC_NAMES = [
    "context_precision",
    "context_recall",
    "context_relevance",
    "context_entity_recall",
]

METRICS_NEEDING_REFERENCE = {"context_precision", "context_recall", "context_entity_recall"}


@dataclass
class RagasMetrics:
    context_precision: ContextPrecision
    context_recall: ContextRecall
    context_relevance: ContextRelevance
    context_entity_recall: ContextEntityRecall

    def all_metrics(self) -> list[tuple[str, Any]]:
        return [
            ("context_precision", self.context_precision),
            ("context_recall", self.context_recall),
            ("context_relevance", self.context_relevance),
            ("context_entity_recall", self.context_entity_recall),
        ]


def load_dataset(path: str) -> list[dict[str, Any]]:
    with open(path) as f:
        data = json.load(f)
    for i, item in enumerate(data):
        if "query" not in item:
            raise ValueError(f"Missing 'query' field in item at index {i}: {item}")
    return data


def generate_sample_dataset(path: str, num_queries: int = 10):
    """Generate a sample dataset with reference fields for Ragas evaluation."""
    queries = [
        {
            "query": "What are the membership benefits?",
            "reference": "Members receive discounts on partner services and priority support.",
        },
        {
            "query": "How to file an insurance claim?",
            "reference": "File claims online, by phone, or by mail within 30 days with policy number and incident details.",
        },
        {
            "query": "What is the waiting period for coverage?",
            "reference": "There is a 30-day waiting period for most coverage types, with exceptions for emergency care.",
        },
        {
            "query": "Are pre-existing conditions covered?",
            "reference": "Pre-existing conditions are covered after a 12-month waiting period unless waived by underwriting.",
        },
        {
            "query": "How to renew my policy?",
            "reference": "Policies auto-renew annually. Manual renewal can be done online, by phone, or through your agent.",
        },
        {
            "query": "What dental services are included?",
            "reference": "Coverage includes routine cleanings, fillings, and major procedures like crowns and root canals.",
        },
        {
            "query": "How are premiums calculated?",
            "reference": "Premiums are based on age, health status, coverage level, and geographic location.",
        },
        {
            "query": "Can I add family members to my plan?",
            "reference": "Family members can be added during open enrollment or within 30 days of a qualifying life event.",
        },
        {
            "query": "What is the refund policy?",
            "reference": "Refunds are issued within 10 business days for cancellations during the free-look period.",
        },
        {
            "query": "How to update personal information?",
            "reference": "Update your address, phone, or email through the member portal or by calling customer service.",
        },
    ]
    sample = queries[:num_queries]
    for item in sample:
        item["lang_tag"] = "en-US"
    with open(path, "w") as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)
    print(f"  Sample dataset ({len(sample)} queries) written to {path}")
    print("  Tip: Edit the 'reference' fields with ground-truth answers for best results.")


def init_ragas_llm():
    registry = ModelRegistry()
    params = cfg.get_llm_params()
    registry.register(
        "llm-default",
        params["provider"],
        params["model"],
        temperature=params["temperature"],
    )
    return registry.get_model("llm-default")


def build_metrics(llm) -> RagasMetrics:
    return RagasMetrics(
        context_precision=ContextPrecision(llm=llm),
        context_recall=ContextRecall(llm=llm),
        context_relevance=ContextRelevance(llm=llm),
        context_entity_recall=ContextEntityRecall(llm=llm),
    )


def build_node(vector_stores: list[VectorStoreManager],
               retrieval_mode: str, enable_rerank: bool) -> RetrievalNode:
    rerank_params = cfg.get_rerank_params()
    vs_params = cfg.get_vector_store_params()

    reranker = DashScopeRerank(top_n=rerank_params["top_n"])

    return RetrievalNode(
        vector_stores=vector_stores,
        reranker=reranker,
        recall_limit=rerank_params["recall_limit"],
        relevance_threshold=rerank_params["relevance_threshold"],
        enable_rerank=enable_rerank,
        retrieval_mode=retrieval_mode,
        top_k=vs_params["top_k"],
    )


def run_retrieval(node: RetrievalNode, query: str,
                  lang_tag: str = "en-US") -> list[dict[str, Any]]:
    state = WorkflowState(vector_store_queries={lang_tag: query})
    result = node(state, {})
    return result.get("retrieved_context", [])


def evaluate_config(node: RetrievalNode, dataset: list[dict[str, Any]],
                    metrics: RagasMetrics, label: str) -> dict[str, Any]:
    scores: dict[str, list[float]] = {name: [] for name in METRIC_NAMES}
    retrieved_counts: list[int] = []
    skipped_no_reference = 0
    failures = 0

    for item in dataset:
        query = item["query"]
        reference = item.get("reference")
        lang_tag = item.get("lang_tag", "en-US")

        retrieved = run_retrieval(node, query, lang_tag)
        retrieved_counts.append(len(retrieved))
        retrieved_texts = [r.get("text", "") for r in retrieved]

        sample = SingleTurnSample(
            user_input=query,
            retrieved_contexts=retrieved_texts,
            reference=reference,
        )

        for metric_name, metric in metrics.all_metrics():
            if metric_name in METRICS_NEEDING_REFERENCE and not reference:
                skipped_no_reference += 1
                continue
            try:
                score = metric.single_turn_score(sample)
                scores[metric_name].append(score)
            except Exception:
                failures += 1

    result: dict[str, Any] = {"config": label, "num_queries": len(dataset)}
    for name in METRIC_NAMES:
        vals = scores[name]
        result[name] = mean(vals) if vals else float("nan")
    result["avg_retrieved"] = mean(retrieved_counts) if retrieved_counts else 0.0
    result["skipped_no_reference"] = skipped_no_reference
    result["failures"] = failures
    return result


def print_report(all_metrics: list[dict[str, Any]]):
    metric_labels = {
        "context_precision": "CtxPrec",
        "context_recall": "CtxRecall",
        "context_relevance": "CtxRelev",
        "context_entity_recall": "CtxEntRcl",
    }

    print("\n" + "=" * 80)
    print("  Retrieval Quality Evaluation Report (Ragas)")
    print("=" * 80)

    header = f"{'Config':<18}"
    for name in METRIC_NAMES:
        header += f" {metric_labels[name]:>10}"
    header += f" {'AvgRet':>8}"
    print(header)
    print("-" * 80)

    for m in all_metrics:
        line = f"{m['config']:<18}"
        for name in METRIC_NAMES:
            val = m.get(name, float("nan"))
            line += f" {val:>10.4f}" if not _is_nan(val) else f" {'NaN':>10}"
        line += f" {m.get('avg_retrieved', 0):>8.1f}"
        print(line)

    print("-" * 80)
    print(f"  Queries evaluated: {all_metrics[0]['num_queries']}")
    print("=" * 80 + "\n")

    valid_prec = [m for m in all_metrics if not _is_nan(m.get("context_precision"))]
    valid_recall = [m for m in all_metrics if not _is_nan(m.get("context_recall"))]
    if valid_prec:
        best_prec = max(valid_prec, key=lambda x: x["context_precision"])
        print(f"  Best Context Precision: {best_prec['config']} ({best_prec['context_precision']:.4f})")
    if valid_recall:
        best_recall = max(valid_recall, key=lambda x: x["context_recall"])
        print(f"  Best Context Recall:    {best_recall['config']} ({best_recall['context_recall']:.4f})")

    for m in all_metrics:
        if m.get("failures"):
            print(f"  ⚠ {m['config']}: {m['failures']} metric failures (NaN)")
        if m.get("skipped_no_reference"):
            print(f"  ⚠ {m['config']}: {m['skipped_no_reference']} metrics skipped (no reference)")


def _is_nan(val) -> bool:
    import math
    return val is None or (isinstance(val, float) and math.isnan(val))


def export_csv(all_metrics: list[dict[str, Any]], path: str):
    fieldnames = ["config", "num_queries", "avg_retrieved"] + METRIC_NAMES
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in all_metrics:
            writer.writerow({k: m.get(k) for k in fieldnames})
    print(f"  Report exported to {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate retrieval quality with Ragas LLM-as-judge metrics"
    )
    parser.add_argument("--dataset", default=SAMPLE_DATASET,
                        help="Path to JSON test dataset (default: sample_test_queries.json)")
    parser.add_argument("--output", default=None,
                        help="CSV file path to export the report")
    parser.add_argument("--generate-sample", action="store_true",
                        help="Generate a sample dataset file and exit")
    parser.add_argument("--lang", default="en-US",
                        help="Default language tag for queries (default: en-US)")
    args = parser.parse_args()

    if args.generate_sample:
        generate_sample_dataset(args.dataset)
        return

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"Dataset not found: {dataset_path}")
        print("Run with --generate-sample to create one, or specify a dataset with --dataset")
        sys.exit(1)

    dataset = load_dataset(str(dataset_path))
    if not dataset:
        print("Dataset is empty.")
        sys.exit(1)

    no_ref_count = sum(1 for item in dataset if not item.get("reference"))
    if no_ref_count:
        plural = "s" if no_ref_count > 1 else ""
        print(f"Warning: {no_ref_count} query/ies without 'reference'. "
              "Context Precision, Context Recall, and Context Entity Recall will be skipped for those.")
        print("Add 'reference' (ground truth answer text) to each query for complete evaluation.")

    for item in dataset:
        item.setdefault("lang_tag", args.lang)

    vs_params = cfg.get_vector_store_params()
    try:
        faq_store = VectorStoreManager(collection_name=vs_params["collection_name"])
        law_store = VectorStoreManager(collection_name=vs_params["law_collection_name"])
        vector_stores = [faq_store, law_store]
    except Exception as e:
        print(f"Error connecting to Milvus: {e}")
        print("Ensure MILVUS_URI and MILVUS_TOKEN are set in .env, and the server is reachable.")
        sys.exit(1)

    print("Initializing LLM for Ragas metrics...")
    llm = init_ragas_llm()
    metrics = build_metrics(llm)

    configs = [
        ("vector-only", False, "vector_only"),
        ("hybrid", False, "hybrid"),
        ("hybrid+rerank", True, "hybrid"),
    ]

    all_metrics = []
    for label, enable_rerank, retrieval_mode in configs:
        print(f"  Evaluating {label}...")
        node = build_node(vector_stores, retrieval_mode, enable_rerank)
        result = evaluate_config(node, dataset, metrics, label)
        all_metrics.append(result)
        print(f"    ✓ {label} — queries={result['num_queries']}, "
              f"avg_retrieved={result['avg_retrieved']:.1f}, "
              f"ctx_precision={result.get('context_precision', float('nan')):.4f}, "
              f"ctx_recall={result.get('context_recall', float('nan')):.4f}")

    print_report(all_metrics)

    if args.output:
        export_csv(all_metrics, args.output)


if __name__ == "__main__":
    main()
