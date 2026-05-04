import json
import math
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

from eval_retrieval_ragas import (
    METRIC_NAMES,
    METRICS_NEEDING_REFERENCE,
    RagasMetrics,
    build_metrics,
    build_node,
    evaluate_config,
    export_csv,
    generate_sample_dataset,
    init_ragas_llm,
    load_dataset,
    print_report,
    run_retrieval,
)


class TestLoadDataset(unittest.TestCase):
    def test_valid_dataset(self):
        data = [
            {"query": "What is X?", "reference": "X is a letter."},
            {"query": "What is Y?"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = load_dataset(path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["query"], "What is X?")
        finally:
            Path(path).unlink()

    def test_missing_query_raises(self):
        data = [{"reference": "Something"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            with self.assertRaises(ValueError) as ctx:
                load_dataset(path)
            self.assertIn("Missing 'query'", str(ctx.exception))
        finally:
            Path(path).unlink()


class TestGenerateSampleDataset(unittest.TestCase):
    def test_generates_valid_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/sample.json"
            generate_sample_dataset(path, num_queries=5)
            data = load_dataset(path)
            self.assertEqual(len(data), 5)
            for item in data:
                self.assertIn("query", item)
                self.assertIn("reference", item)
                self.assertIn("lang_tag", item)
                self.assertIsInstance(item["reference"], str)
                self.assertTrue(len(item["reference"]) > 0)


class TestInitRagasLLM(unittest.TestCase):
    @patch("eval_retrieval_ragas.ModelRegistry")
    @patch("eval_retrieval_ragas.cfg")
    def test_registers_and_returns_llm(self, mock_cfg, mock_registry_cls):
        mock_cfg.get_llm_params.return_value = {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "temperature": 0.7,
        }
        mock_registry = MagicMock()
        mock_registry_cls.return_value = mock_registry
        mock_registry.get_model.return_value = "fake-llm"

        llm = init_ragas_llm()

        mock_registry.register.assert_called_once_with(
            "llm-default", "deepseek", "deepseek-chat", temperature=0.7
        )
        mock_registry.get_model.assert_called_once_with("llm-default")
        self.assertEqual(llm, "fake-llm")


class TestBuildMetrics(unittest.TestCase):
    @patch("eval_retrieval_ragas.ContextPrecision")
    @patch("eval_retrieval_ragas.ContextRecall")
    @patch("eval_retrieval_ragas.ContextRelevance")
    @patch("eval_retrieval_ragas.ContextEntityRecall")
    def test_returns_ragas_metrics_with_all_four(
        self, mock_cer, mock_cr, mock_crec, mock_cp
    ):
        metrics = build_metrics(llm="fake-llm")
        self.assertIsInstance(metrics, RagasMetrics)
        names = [name for name, _ in metrics.all_metrics()]
        self.assertEqual(names, METRIC_NAMES)
        mock_cp.assert_called_once_with(llm="fake-llm")
        mock_crec.assert_called_once_with(llm="fake-llm")
        mock_cer.assert_called_once_with(llm="fake-llm")
        mock_cr.assert_called_once_with(llm="fake-llm")


class TestBuildNode(unittest.TestCase):
    @patch("eval_retrieval_ragas.cfg")
    @patch("eval_retrieval_ragas.DashScopeRerank")
    def test_build_node_vector_only(self, mock_reranker_cls, mock_cfg):
        mock_cfg.get_rerank_params.return_value = {
            "top_n": 3, "recall_limit": 15, "relevance_threshold": 0.1,
        }
        mock_cfg.get_vector_store_params.return_value = {"top_k": 3}
        mock_reranker = MagicMock()
        mock_reranker_cls.return_value = mock_reranker

        node = build_node([], "vector_only", False)

        self.assertEqual(node.retrieval_mode, "vector_only")
        self.assertFalse(node.enable_rerank)

    @patch("eval_retrieval_ragas.cfg")
    @patch("eval_retrieval_ragas.DashScopeRerank")
    def test_build_node_hybrid_rerank(self, mock_reranker_cls, mock_cfg):
        mock_cfg.get_rerank_params.return_value = {
            "top_n": 3, "recall_limit": 15, "relevance_threshold": 0.1,
        }
        mock_cfg.get_vector_store_params.return_value = {"top_k": 3}
        mock_reranker = MagicMock()
        mock_reranker_cls.return_value = mock_reranker

        node = build_node([], "hybrid", True)

        self.assertEqual(node.retrieval_mode, "hybrid")
        self.assertTrue(node.enable_rerank)


class TestRunRetrieval(unittest.TestCase):
    def test_returns_retrieved_context(self):
        node = MagicMock()
        node.return_value = {"retrieved_context": [{"text": "chunk1"}, {"text": "chunk2"}]}

        results = run_retrieval(node, "test query", "zh-CN")

        self.assertEqual(results, [{"text": "chunk1"}, {"text": "chunk2"}])
        call_state = node.call_args[0][0]
        self.assertEqual(call_state.vector_store_queries, {"zh-CN": "test query"})


class TestEvaluateConfig(unittest.TestCase):
    @dataclass
    class _FakeMetric:
        """Metric that returns a fixed score based on sample data."""
        name: str

        def single_turn_score(self, sample):
            return 0.75

    @dataclass
    class _FailingMetric:
        name: str

        def single_turn_score(self, sample):
            raise RuntimeError("API error")

    def setUp(self):
        self.dataset = [
            {"query": "Q1", "reference": "Answer 1", "lang_tag": "en-US"},
            {"query": "Q2", "reference": "Answer 2", "lang_tag": "zh-CN"},
        ]

    def _make_node(self):
        node = MagicMock()
        node.side_effect = [
            {"retrieved_context": [{"text": "ctx1"}, {"text": "ctx2"}]},
            {"retrieved_context": [{"text": "ctx3"}]},
        ]
        return node

    def test_computes_all_metrics(self):
        node = self._make_node()
        metrics = RagasMetrics(
            context_precision=self._FakeMetric("context_precision"),
            context_recall=self._FakeMetric("context_recall"),
            context_relevance=self._FakeMetric("context_relevance"),
            context_entity_recall=self._FakeMetric("context_entity_recall"),
        )

        result = evaluate_config(node, self.dataset, metrics, "test-config")

        self.assertEqual(result["config"], "test-config")
        self.assertEqual(result["num_queries"], 2)
        self.assertAlmostEqual(result["context_precision"], 0.75)
        self.assertAlmostEqual(result["context_recall"], 0.75)
        self.assertAlmostEqual(result["context_relevance"], 0.75)
        self.assertAlmostEqual(result["context_entity_recall"], 0.75)

    def test_missing_reference_skips_metrics(self):
        node = self._make_node()
        dataset = [{"query": "Q1"}]  # no reference
        metrics = RagasMetrics(
            context_precision=self._FakeMetric("context_precision"),
            context_recall=self._FakeMetric("context_recall"),
            context_relevance=self._FakeMetric("context_relevance"),
            context_entity_recall=self._FakeMetric("context_entity_recall"),
        )

        result = evaluate_config(node, dataset, metrics, "no-ref")

        self.assertEqual(result["skipped_no_reference"], 3)  # prec, recall, ent_recall
        self.assertFalse(math.isnan(result["context_relevance"]))  # doesn't need ref

    def test_failure_yields_nan(self):
        node = self._make_node()
        metrics = RagasMetrics(
            context_precision=self._FailingMetric("context_precision"),
            context_recall=self._FakeMetric("context_recall"),
            context_relevance=self._FakeMetric("context_relevance"),
            context_entity_recall=self._FakeMetric("context_entity_recall"),
        )

        result = evaluate_config(node, [self.dataset[0]], metrics, "failing")

        self.assertTrue(math.isnan(result["context_precision"]))
        self.assertAlmostEqual(result["context_recall"], 0.75)
        self.assertEqual(result["failures"], 1)


class TestPrintReport(unittest.TestCase):
    def test_prints_table(self):
        all_metrics = [
            {
                "config": "vector-only",
                "num_queries": 2,
                "context_precision": 0.61,
                "context_recall": 0.58,
                "context_relevance": 0.72,
                "context_entity_recall": 0.45,
                "avg_retrieved": 12.3,
                "skipped_no_reference": 0,
                "failures": 0,
            },
            {
                "config": "hybrid+rerank",
                "num_queries": 2,
                "context_precision": 0.81,
                "context_recall": 0.55,
                "context_relevance": 0.89,
                "context_entity_recall": 0.40,
                "avg_retrieved": 5.1,
                "skipped_no_reference": 0,
                "failures": 0,
            },
        ]

        with patch("builtins.print") as mock_print:
            print_report(all_metrics)

        output = "\n".join(str(call[0][0]) for call in mock_print.call_args_list)
        self.assertIn("vector-only", output)
        self.assertIn("hybrid+rerank", output)
        self.assertIn("Best Context Precision", output)
        self.assertIn("Best Context Recall", output)

    def test_nan_values_display(self):
        all_metrics = [
            {
                "config": "bad-config",
                "num_queries": 1,
                "context_precision": float("nan"),
                "context_recall": float("nan"),
                "context_relevance": 0.5,
                "context_entity_recall": float("nan"),
                "avg_retrieved": 0.0,
                "skipped_no_reference": 0,
                "failures": 3,
            },
        ]

        with patch("builtins.print") as mock_print:
            print_report(all_metrics)

        output = "\n".join(str(call[0][0]) for call in mock_print.call_args_list)
        self.assertIn("NaN", output)
        self.assertIn("bad-config", output)
        self.assertIn("metric failures", output)


class TestExportCSV(unittest.TestCase):
    def test_writes_csv(self):
        all_metrics = [
            {
                "config": "hybrid",
                "num_queries": 2,
                "avg_retrieved": 10.0,
                "context_precision": 0.68,
                "context_recall": 0.63,
                "context_relevance": 0.78,
                "context_entity_recall": 0.44,
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/report.csv"
            export_csv(all_metrics, path)

            with open(path) as f:
                content = f.read()

            self.assertIn("config", content)
            self.assertIn("context_precision", content)
            self.assertIn("hybrid", content)
            self.assertIn("0.68", content)


class TestRagasMetricsDataclass(unittest.TestCase):
    def test_all_metrics_returns_correct_order(self):
        fake = MagicMock()
        m = RagasMetrics(
            context_precision=fake,
            context_recall=fake,
            context_relevance=fake,
            context_entity_recall=fake,
        )
        names = [name for name, _ in m.all_metrics()]
        self.assertEqual(names, [
            "context_precision",
            "context_recall",
            "context_relevance",
            "context_entity_recall",
        ])


class TestMetricsNeedingReference(unittest.TestCase):
    def test_correct_metrics_need_reference(self):
        self.assertIn("context_precision", METRICS_NEEDING_REFERENCE)
        self.assertIn("context_recall", METRICS_NEEDING_REFERENCE)
        self.assertIn("context_entity_recall", METRICS_NEEDING_REFERENCE)
        self.assertNotIn("context_relevance", METRICS_NEEDING_REFERENCE)


if __name__ == "__main__":
    unittest.main()
