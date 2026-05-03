import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

from muggle.core.graph_processor import GraphProcessor
from muggle.core.state import WorkflowState
from muggle.core.guard import IntentCheckResult
from muggle.core.response import InquiryResult
from muggle.core.search import QueryRewriteResult
from muggle.core.validate import ValidationResult
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
        vector_store.search.return_value = [{"header": "Test Header", "text": "Test Content"}]
        
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
            QueryRewriteResult(vector_store_query="rewritten query"),
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
        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry, vector_store=vector_store)

        # 4. Execute
        response = processor.get_response("Hello, tell me more about insurance", thread_id="rag_test")
        
        # 5. Assertions
        self.assertEqual(response, "Final grounded answer")
        
        # Verify Vector Store was called with rewritten query (dual-vector search)
        self.assertEqual(vector_store.search.call_count, 2)
        vector_store.search.assert_any_call(query_text="rewritten query", vector_field="content_vector", limit=15)
        vector_store.search.assert_any_call(query_text="rewritten query", vector_field="header_vector", limit=15)
        
        # Verify Inquiry prompt was rendered with context (second-to-last call; last is validate)
        inquiry_call = prompt_registry.get_system_prompt.call_args_list[-2]
        self.assertIn("Test Header", inquiry_call[1]["variables"]["context"])
        self.assertIn("Test Content", inquiry_call[1]["variables"]["context"])

if __name__ == '__main__':
    unittest.main()
