import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

from muggle.core.graph_processor import GraphProcessor
from muggle.core.state import WorkflowState
from muggle.core.guard import IntentCheckResult
from muggle.core.response import InquiryResult
from muggle.core.search import QueryRewriteResult
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


if __name__ == '__main__':
    unittest.main()
