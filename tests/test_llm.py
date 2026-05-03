import unittest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage
from muggle.core.graph_processor import GraphProcessor
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import STR_LLM_DEFAULT


class TestGraphProcessor(unittest.TestCase):
    @patch('muggle.infra.registry.model.init_chat_model')
    @patch('muggle.core.graph_processor.create_agent')
    def test_multi_turn_memory(self, mock_create_agent, mock_init_model):
        # Setup mock registries
        model_registry = ModelRegistry()
        model_registry.register(STR_LLM_DEFAULT, provider="test", model_id="test", temperature=0)
        
        prompt_registry = MagicMock(spec=PromptRegistry)
        prompt_registry.get_system_prompt.return_value = "System"
        
        # Setup mock agent
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance
        
        # Turn 1
        mock_agent_instance.invoke.return_value = {
            "structured_response": {"pass_intent_check": True, "response": "Response 1", "vector_store_query": "Query 1"},
            "messages": [AIMessage(content="Response 1")]
        }
        
        vector_store = MagicMock(spec=VectorStoreManager)
        vector_store.search.return_value = []
        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry, vector_store=vector_store)
        processor.warm_up()
        
        resp1 = processor.get_response("Turn 1", thread_id="t1")
        self.assertEqual(resp1, "Response 1")
        
        # Verify first invocation had 1 message (the human input)
        first_call_state = mock_agent_instance.invoke.call_args_list[0][0][0]
        self.assertEqual(len(first_call_state.messages), 1)
        
        # Turn 2
        mock_agent_instance.invoke.return_value = {
            "structured_response": {"pass_intent_check": True, "response": "Response 2", "vector_store_query": "Query 2"},
            "messages": [AIMessage(content="Response 2")]
        }
        
        resp2 = processor.get_response("Turn 2", thread_id="t1")
        self.assertEqual(resp2, "Response 2")
        
        # Verify TURN 2 invocation has HISTORY (should be 3 messages now: H1, A1, H2)
        last_call_state = mock_agent_instance.invoke.call_args_list[-1][0][0]
        self.assertGreater(len(last_call_state.messages), 1)
        
        # Check if Turn 1 message is in Turn 2's state
        contents = [m.content for m in last_call_state.messages]
        self.assertIn("Turn 1", contents)
        self.assertIn("Response 1", contents)
        self.assertIn("Turn 2", contents)

if __name__ == '__main__':
    unittest.main()
