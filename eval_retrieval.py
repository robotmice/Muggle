#!/usr/bin/env python3
"""One-click retrieval quality evaluation script.

Compares three configurations:
  1. vector-only  — dense ANN search only
  2. hybrid        — dense + sparse (BM25) with RRF fusion, no rerank
  3. hybrid+rerank — hybrid retrieval + DashScope rerank + relevance threshold

Usage:
  poetry run python eval_retrieval.py
  poetry run python eval_retrieval.py --dataset sample_test_queries.json
  poetry run python eval_retrieval.py --k 5 --output report.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean
from typing import List, Dict, Any

from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank

from muggle.core.search.retrieval import RetrievalNode
from muggle.core.state import WorkflowState
from muggle.infra.config import cfg
from muggle.infra.registry import VectorStoreManager

SAMPLE_DATASET = "sample_test_queries.json"


def load_dataset(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        data = json.load(f)
    for item in data:
        if "query" not in item:
            raise ValueError(f"Missing 'query' field in item: {item}")
    return data


def build_node(vector_stores: list[VectorStoreManager],
               retrieval_mode: str, enable_rerank: bool) -> RetrievalNode:
    rerank_params = cfg.get_rerank_params()
    vs_params = cfg.get_vector_store_params()

    if enable_rerank:
        reranker = DashScopeRerank(top_n=rerank_params["top_n"])
    else:
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
                  lang_tag: str = "en-US") -> List[Dict[str, Any]]:
    state = WorkflowState(vector_store_queries={lang_tag: query})
    result = node(state, {})
    return result.get("retrieved_context", [])


def precision_at_k(retrieved_ids: List[str], relevant_ids: set[str], k: int) -> float:
    if k <= 0 or not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / k


def recall_at_k(retrieved_ids: List[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)


def mrr(retrieved_ids: List[str], relevant_ids: set[str]) -> float:
    for i, rid in enumerate(retrieved_ids, start=1):
        if rid in relevant_ids:
            return 1.0 / i
    return 0.0


def dcg_at_k(retrieved_ids: List[str], relevant_ids: set[str], k: int) -> float:
    import math
    dcg = 0.0
    for i, rid in enumerate(retrieved_ids[:k], start=1):
        if rid in relevant_ids:
            dcg += 1.0 / math.log2(i + 1)
    return dcg


def ndcg_at_k(retrieved_ids: List[str], relevant_ids: set[str], k: int) -> float:
    ideal = dcg_at_k(list(relevant_ids)[:k], relevant_ids, k)
    if ideal == 0:
        return 0.0
    return dcg_at_k(retrieved_ids, relevant_ids, k) / ideal


def compute_metrics(all_results: List[tuple[str, List[Dict[str, Any]]]],
                    k_values: List[int]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    for k in k_values:
        metrics[f"P@{k}"] = mean(
            precision_at_k(ids, rels, k) for ids, rels, _, _ in all_results
        )
        metrics[f"R@{k}"] = mean(
            recall_at_k(ids, rels, k) for ids, rels, _, _ in all_results
        )
        metrics[f"nDCG@{k}"] = mean(
            ndcg_at_k(ids, rels, k) for ids, rels, _, _ in all_results
        )
    metrics["MRR"] = mean(mrr(ids, rels) for ids, rels, _, _ in all_results)

    # Average retrieved count
    metrics["avg_retrieved"] = mean(
        len(res) for _, _, _, res in all_results
    ) if all_results else 0.0

    return metrics


def evaluate_config(node: RetrievalNode, dataset: List[Dict[str, Any]],
                    k_values: List[int], label: str) -> Dict[str, Any]:
    all_results = []
    for item in dataset:
        query = item["query"]
        relevant_ids = set(item.get("relevant_ids", []))
        # If dataset doesn't specify lang_tag, try both and collect IDs
        lang_tag = item.get("lang_tag", "en-US")
        retrieved = run_retrieval(node, query, lang_tag)
        retrieved_ids = [
            r.get("id", r.get("text", ""))
            for r in retrieved
        ]
        all_results.append((retrieved_ids, relevant_ids, query, retrieved))

    metrics = compute_metrics(all_results, k_values)
    metrics["config"] = label
    metrics["num_queries"] = len(dataset)
    return metrics


def print_report(all_metrics: List[Dict[str, Any]], k_values: List[int]):
    print("\n" + "=" * 70)
    print("  Retrieval Quality Evaluation Report")
    print("=" * 70)

    header = f"{'Config':<18}"
    for k in k_values:
        header += f" {'P@'+str(k):>8} {'R@'+str(k):>8} {'nDCG@'+str(k):>8}"
    header += f" {'MRR':>8} {'AvgRet':>8}"
    print(header)
    print("-" * 70)

    for m in all_metrics:
        line = f"{m['config']:<18}"
        for k in k_values:
            line += f" {m.get(f'P@{k}', 0):>8.4f} {m.get(f'R@{k}', 0):>8.4f} {m.get(f'nDCG@{k}', 0):>8.4f}"
        line += f" {m.get('MRR', 0):>8.4f} {m.get('avg_retrieved', 0):>8.1f}"
        print(line)

    print("-" * 70)
    print(f"  Queries evaluated: {all_metrics[0]['num_queries']}")
    print("=" * 70 + "\n")

    # Highlight the best
    best_mrr = max(m, key=lambda x: x.get("MRR", 0))
    print(f"  Best MRR: {best_mrr['config']} ({best_mrr['MRR']:.4f})")
    if k_values:
        best_pk = max(m, key=lambda x: x.get(f"P@{k_values[0]}", 0))
        print(f"  Best P@{k_values[0]}: {best_pk['config']} ({best_pk[f'P@{k_values[0]}']:.4f})")


def export_csv(all_metrics: List[Dict[str, Any]], k_values: List[int], path: str):
    fieldnames = ["config", "num_queries", "avg_retrieved"]
    for k in k_values:
        fieldnames += [f"P@{k}", f"R@{k}", f"nDCG@{k}"]
    fieldnames.append("MRR")

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in all_metrics:
            writer.writerow({k: m.get(k) for k in fieldnames})
    print(f"  Report exported to {path}")


def generate_sample_dataset(path: str, num_queries: int = 10):
    """Generate a sample dataset for evaluation."""
    queries = [
        "What are the membership benefits?",
        "How to file an insurance claim?",
        "What is the waiting period for coverage?",
        "Are pre-existing conditions covered?",
        "How to renew my policy?",
        "What dental services are included?",
        "How are premiums calculated?",
        "Can I add family members to my plan?",
        "What is the refund policy?",
        "How to update personal information?",
    ]
    sample = [
        {"query": q, "relevant_ids": []}
        for q in queries[:num_queries]
    ]
    with open(path, "w") as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)
    print(f"  Sample dataset ({num_queries} queries) written to {path}")
    print("  Tip: Fill in 'relevant_ids' for each query to enable metric computation.")
    print("       IDs should match the 'id' field in your Milvus collection.")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate retrieval quality across vector-only, hybrid, and hybrid+rerank"
    )
    parser.add_argument("--dataset", default=SAMPLE_DATASET,
                        help="Path to JSON test dataset (default: sample_test_queries.json)")
    parser.add_argument("--k", type=int, nargs="+", default=[3, 5],
                        help="Cutoff values for P@k, R@k, nDCG@k (default: 3 5)")
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

    # Load dataset
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"Dataset not found: {dataset_path}")
        print("Run with --generate-sample to create one, or specify a dataset with --dataset")
        sys.exit(1)

    dataset = load_dataset(str(dataset_path))
    if not dataset:
        print("Dataset is empty.")
        sys.exit(1)

    has_relevance = any(item.get("relevant_ids") for item in dataset)
    if not has_relevance:
        print("Warning: No 'relevant_ids' found in dataset. Metrics will be 0.0.")
        print("Add 'relevant_ids' (list of doc IDs) to each query in the dataset.")

    # Apply lang_tag default
    for item in dataset:
        item.setdefault("lang_tag", args.lang)

    # Initialize vector stores
    vs_params = cfg.get_vector_store_params()
    try:
        faq_store = VectorStoreManager(collection_name=vs_params["collection_name"])
        law_store = VectorStoreManager(collection_name=vs_params["law_collection_name"])
        vector_stores = [faq_store, law_store]
    except Exception as e:
        print(f"Error connecting to Milvus: {e}")
        print("Ensure MILVUS_URI and MILVUS_TOKEN are set in .env, and the server is reachable.")
        sys.exit(1)

    k_values = sorted(args.k)
    configs = [
        ("vector-only", False, "vector_only"),
        ("hybrid", False, "hybrid"),
        ("hybrid+rerank", True, "hybrid"),
    ]

    all_metrics = []
    for label, enable_rerank, retrieval_mode in configs:
        node = build_node(vector_stores, retrieval_mode, enable_rerank)
        metrics = evaluate_config(node, dataset, k_values, label)
        all_metrics.append(metrics)
        print(f"  ✓ {label} — {metrics['num_queries']} queries, "
              f"avg_retrieved={metrics['avg_retrieved']:.1f}, MRR={metrics['MRR']:.4f}")

    print_report(all_metrics, k_values)

    if args.output:
        export_csv(all_metrics, k_values, args.output)


if __name__ == "__main__":
    main()
