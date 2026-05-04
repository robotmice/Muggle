import unittest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from muggle.core.graph_processor import GraphProcessor
from muggle.core.guard import IntentCheckResult
from muggle.core.response import InquiryResult
from muggle.core.search import QueryRewriteResult
from muggle.core.validation import ValidationResult
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import STR_LLM_DEFAULT


class TestGraphProcessor(unittest.TestCase):
    @patch('muggle.infra.registry.model.init_chat_model')
    def test_multi_turn_memory(self, mock_init_model):
        # Setup mock registries
        model_registry = ModelRegistry()
        model_registry.register(STR_LLM_DEFAULT, provider="test", model_id="test", temperature=0)
        
        prompt_registry = MagicMock(spec=PromptRegistry)
        prompt_registry.get_system_prompt.return_value = "System"
        
        # Setup mock model
        mock_model = MagicMock()
        mock_init_model.return_value = mock_model
        
        mock_structured_model = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured_model
        
        # Results for Turn 1 and Turn 2
        results = [
            IntentCheckResult(pass_intent_check=True),
            QueryRewriteResult(query_zh="Query 1 zh", query_en="Query 1 en"),
            InquiryResult(response="Response 1"),
            ValidationResult(pass_validation=True),
            IntentCheckResult(pass_intent_check=True),
            QueryRewriteResult(query_zh="Query 2 zh", query_en="Query 2 en"),
            InquiryResult(response="Response 2"),
            ValidationResult(pass_validation=True),
        ]
        mock_structured_model.invoke.side_effect = results
        
        vector_store = MagicMock(spec=VectorStoreManager)
        vector_store.hybrid_search.return_value = []
        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry, vector_store=vector_store)

        # Turn 1
        resp1 = processor.get_response("Turn 1", thread_id="t1")
        self.assertEqual(resp1, "Response 1")
        
        # Verify first invocation (intent check) had 2 messages: System + Human
        first_call_msgs = mock_structured_model.invoke.call_args_list[0][0][0]
        self.assertEqual(len(first_call_msgs), 2)
        self.assertIsInstance(first_call_msgs[0], SystemMessage)
        self.assertIsInstance(first_call_msgs[1], HumanMessage)
        
        # Turn 2
        resp2 = processor.get_response("Turn 2", thread_id="t1")
        self.assertEqual(resp2, "Response 2")
        
        # Verify TURN 2 invocation has HISTORY
        # Second-to-last structured output call is inquiry_node of Turn 2 (last is validate).
        # Messages should be: System, Human 1, AI 1, Human 2
        inquiry_call_index = -2
        last_call_msgs = mock_structured_model.invoke.call_args_list[inquiry_call_index][0][0]
        self.assertEqual(len(last_call_msgs), 4)
        
        contents = [m.content for m in last_call_msgs]
        self.assertIn("Turn 1", contents)
        self.assertIn("Response 1", contents)
        self.assertIn("Turn 2", contents)

if __name__ == '__main__':
    unittest.main()
