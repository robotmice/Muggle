import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

from muggle.core.graph_processor import GraphProcessor
from muggle.core.state import WorkflowState
from muggle.core.guard import IntentCheckResult
from muggle.core.response import InquiryResult
from muggle.core.search import QueryRewriteResult, RetrievalNode
from muggle.core.validation import ValidationResult
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import STR_LLM_DEFAULT

class TestRAGFlow(unittest.TestCase):
    @patch('muggle.core.graph_processor.DashScopeRerank')
    @patch('muggle.infra.registry.model.init_chat_model')
    def test_full_rag_pipeline(self, mock_init_model, mock_reranker_cls):
        # 1. Setup Mock Registries
        model_registry = ModelRegistry()
        model_registry.register(STR_LLM_DEFAULT, provider="test", model_id="test", temperature=0)
        
        prompt_registry = MagicMock(spec=PromptRegistry)
        prompt_registry.get_system_prompt.side_effect = lambda name, variables=None: f"Prompt for {name} with context {variables.get('context') if variables else None}"
        
        vector_store = MagicMock(spec=VectorStoreManager)
        vector_store.hybrid_search.return_value = [{"id": "abc123", "header": "Test Header", "text": "Test Content"}]
        
        # 2. Setup Mock Model
        mock_model = MagicMock()
        mock_init_model.return_value = mock_model
        
        mock_structured_model = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured_model
        
        # Sequence of LLM responses: Intent Check -> Query Rewrite -> Inquiry -> Validate
        mock_structured_model.invoke.side_effect = [
            # 1. Intent Check
            IntentCheckResult(pass_intent_check=True),
            # 2. Query Rewrite
            QueryRewriteResult(query_zh="rewritten query zh", query_en="rewritten query en"),
            # 3. Inquiry
            InquiryResult(response="Final grounded answer"),
            # 4. Validate
            ValidationResult(pass_validation=True),
        ]
        
        # 2.5 Setup Mock Reranker — returns docs with relevance_score ≥ threshold
        mock_reranker = MagicMock()
        mock_reranker.compress_documents.return_value = [
            Document(page_content="Test Content", metadata={"header": "Test Header", "is_segment": False, "relevance_score": 0.9})
        ]
        mock_reranker_cls.return_value = mock_reranker

        # 3. Initialize Processor
        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry, vector_stores=[vector_store])

        # 4. Execute
        response = processor.get_response("Hello, tell me more about insurance", thread_id="rag_test")
        
        # 5. Assertions
        self.assertEqual(response, "Final grounded answer")
        
        # Verify Vector Store hybrid_search was called per language with lang_tag filter
        self.assertEqual(vector_store.hybrid_search.call_count, 2)
        vector_store.hybrid_search.assert_any_call(
            query_text="rewritten query zh", limit=15, filter='lang_tag == "zh-CN"'
        )
        vector_store.hybrid_search.assert_any_call(
            query_text="rewritten query en", limit=15, filter='lang_tag == "en-US"'
        )
        
        # Verify Inquiry prompt was rendered with context (second-to-last call; last is validate)
        inquiry_call = prompt_registry.get_system_prompt.call_args_list[-2]
        self.assertIn("Test Header", inquiry_call[1]["variables"]["context"])
        self.assertIn("Test Content", inquiry_call[1]["variables"]["context"])


class TestRetrievalDedup(unittest.TestCase):
    """Test that RetrievalNode correctly deduplicates results across language searches."""

    @patch('muggle.core.graph_processor.DashScopeRerank')
    @patch('muggle.infra.registry.model.init_chat_model')
    def test_dedup_across_languages(self, mock_init_model, mock_reranker_cls):
        model_registry = ModelRegistry()
        model_registry.register(STR_LLM_DEFAULT, provider="test", model_id="test", temperature=0)

        prompt_registry = MagicMock(spec=PromptRegistry)
        prompt_registry.get_system_prompt.side_effect = lambda name, variables=None: f"Prompt for {name} with context {variables.get('context') if variables else None}"

        vector_store = MagicMock(spec=VectorStoreManager)
        # Both language searches return overlapping results (same id="shared")
        vector_store.hybrid_search.side_effect = [
            [{"id": "shared", "header": "Shared Header", "text": "Shared Content"}],
            [{"id": "shared", "header": "Shared Header", "text": "Shared Content"},
             {"id": "unique", "header": "Unique EN", "text": "English-only content"}],
        ]

        mock_model = MagicMock()
        mock_init_model.return_value = mock_model
        mock_structured_model = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured_model

        mock_structured_model.invoke.side_effect = [
            IntentCheckResult(pass_intent_check=True),
            QueryRewriteResult(query_zh="query zh", query_en="query en"),
            InquiryResult(response="Grounded answer"),
            ValidationResult(pass_validation=True),
        ]

        mock_reranker = MagicMock()
        mock_reranker.compress_documents.return_value = [
            Document(page_content="Shared Content", metadata={"header": "Shared Header", "is_segment": False, "relevance_score": 0.9}),
            Document(page_content="English-only content", metadata={"header": "Unique EN", "is_segment": False, "relevance_score": 0.8}),
        ]
        mock_reranker_cls.return_value = mock_reranker

        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry, vector_stores=[vector_store])
        response = processor.get_response("test query", thread_id="dedup_test")

        self.assertEqual(response, "Grounded answer")
        # hybrid_search called twice (zh-CN + en-US)
        self.assertEqual(vector_store.hybrid_search.call_count, 2)
        # Reranker received 2 unique docs (not 3 — "shared" was deduplicated)
        docs_passed_to_reranker = mock_reranker.compress_documents.call_args[1]["documents"]
        self.assertEqual(len(docs_passed_to_reranker), 2,
                         f"Expected 2 docs after dedup, got {len(docs_passed_to_reranker)}")
        doc_ids = [d.metadata.get("header") for d in docs_passed_to_reranker]
        self.assertIn("Shared Header", doc_ids)
        self.assertIn("Unique EN", doc_ids)


class TestRetrievalModes(unittest.TestCase):
    """Test retrieval mode switching and reranker toggle."""

    def setUp(self):
        self.vector_store = MagicMock(spec=VectorStoreManager)
        self.vector_store.search.return_value = [
            {"id": "d1", "header": "H1", "text": "Result 1", "is_segment": False},
            {"id": "d2", "header": "H2", "text": "Result 2", "is_segment": False},
            {"id": "d3", "header": "H3", "text": "Result 3", "is_segment": False},
        ]
        self.vector_store.hybrid_search.return_value = [
            {"id": "h1", "header": "HH1", "text": "Hybrid 1", "is_segment": False},
            {"id": "h2", "header": "HH2", "text": "Hybrid 2", "is_segment": False},
        ]

    def test_vector_only_mode_uses_search(self):
        node = RetrievalNode(
            vector_stores=[self.vector_store],
            reranker=MagicMock(),
            recall_limit=10, relevance_threshold=0.5,
            enable_rerank=False, retrieval_mode="vector_only", top_k=3,
        )
        state = WorkflowState(vector_store_queries={"en-US": "test query"})
        result = node(state, {})

        self.vector_store.search.assert_called_once_with(
            query_text="test query", limit=3, filter='lang_tag == "en-US"'
        )
        self.vector_store.hybrid_search.assert_not_called()
        self.assertEqual(len(result["retrieved_context"]), 3)

    def test_hybrid_mode_uses_hybrid_search(self):
        node = RetrievalNode(
            vector_stores=[self.vector_store],
            reranker=MagicMock(),
            recall_limit=10, relevance_threshold=0.5,
            enable_rerank=False, retrieval_mode="hybrid", top_k=2,
        )
        state = WorkflowState(vector_store_queries={"zh-CN": "测试"})
        result = node(state, {})

        self.vector_store.hybrid_search.assert_called_once_with(
            query_text="测试", limit=2, filter='lang_tag == "zh-CN"'
        )
        self.vector_store.search.assert_not_called()
        self.assertEqual(len(result["retrieved_context"]), 2)

    def test_rerank_disabled_skips_compressor(self):
        reranker = MagicMock()
        node = RetrievalNode(
            vector_stores=[self.vector_store],
            reranker=reranker,
            recall_limit=10, relevance_threshold=0.5,
            enable_rerank=False, retrieval_mode="hybrid", top_k=2,
        )
        state = WorkflowState(vector_store_queries={"en-US": "test"})
        node(state, {})

        reranker.compress_documents.assert_not_called()

    def test_rerank_enabled_calls_compressor(self):
        reranker = MagicMock()
        reranker.compress_documents.return_value = [
            Document(page_content="Hybrid 1", metadata={"header": "HH1", "is_segment": False, "relevance_score": 0.9}),
        ]
        node = RetrievalNode(
            vector_stores=[self.vector_store],
            reranker=reranker,
            recall_limit=10, relevance_threshold=0.5,
            enable_rerank=True, retrieval_mode="hybrid", top_k=2,
        )
        state = WorkflowState(vector_store_queries={"en-US": "test"})
        result = node(state, {})

        reranker.compress_documents.assert_called_once()
        self.assertEqual(len(result["retrieved_context"]), 1)
        self.assertEqual(result["retrieved_context"][0]["relevance_score"], 0.9)

    def test_rerank_threshold_filters_results(self):
        reranker = MagicMock()
        reranker.compress_documents.return_value = [
            Document(page_content="High", metadata={"header": "H", "is_segment": False, "relevance_score": 0.9}),
            Document(page_content="Low", metadata={"header": "L", "is_segment": False, "relevance_score": 0.3}),
            Document(page_content="Zero", metadata={"header": "Z", "is_segment": False, "relevance_score": 0.0}),
        ]
        node = RetrievalNode(
            vector_stores=[self.vector_store],
            reranker=reranker,
            recall_limit=10, relevance_threshold=0.5,
            enable_rerank=True, retrieval_mode="hybrid", top_k=3,
        )
        state = WorkflowState(vector_store_queries={"en-US": "test"})
        result = node(state, {})

        self.assertEqual(len(result["retrieved_context"]), 1)
        self.assertEqual(result["retrieved_context"][0]["text"], "High")


class TestEvalMetrics(unittest.TestCase):
    """Verify evaluation metric functions used in eval_retrieval.py."""

    def test_precision_at_k(self):
        from eval_retrieval import precision_at_k
        relevant = {"a", "b", "c"}
        self.assertAlmostEqual(precision_at_k(["a", "x", "y"], relevant, 3), 1 / 3)
        self.assertAlmostEqual(precision_at_k(["a", "b", "c"], relevant, 3), 1.0)
        self.assertAlmostEqual(precision_at_k(["x", "y", "z"], relevant, 3), 0.0)
        self.assertAlmostEqual(precision_at_k([], relevant, 3), 0.0)

    def test_recall_at_k(self):
        from eval_retrieval import recall_at_k, precision_at_k
        relevant = {"a", "b", "c", "d"}
        self.assertAlmostEqual(recall_at_k(["a", "x"], relevant, 2), 0.25)
        self.assertAlmostEqual(recall_at_k(["a", "b", "c", "d"], relevant, 4), 1.0)
        self.assertAlmostEqual(recall_at_k([], relevant, 3), 0.0)

    def test_mrr(self):
        from eval_retrieval import mrr
        relevant = {"c"}
        self.assertAlmostEqual(mrr(["a", "b", "c", "d"], relevant), 1 / 3)
        self.assertAlmostEqual(mrr(["c", "a", "b"], relevant), 1.0)
        self.assertAlmostEqual(mrr(["a", "b"], relevant), 0.0)

    def test_ndcg_at_k(self):
        from eval_retrieval import ndcg_at_k
        relevant = {"a", "c"}
        score = ndcg_at_k(["a", "b", "c"], relevant, 3)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertAlmostEqual(ndcg_at_k(["a", "b", "c"], {"a", "b", "c"}, 3), 1.0)
        self.assertAlmostEqual(ndcg_at_k(["x", "y"], relevant, 3), 0.0)


if __name__ == '__main__':
    unittest.main()
