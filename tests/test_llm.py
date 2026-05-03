import unittest
from unittest.mock import MagicMock, patch

from muggle.core.processor import ChatProcessor
from muggle.infra.registry import ModelRegistry, PromptRegistry
from muggle.shared.constants import STR_LLM_DEFAULT, STR_PROMPT_DEFAULT


class TestChatProcessor(unittest.TestCase):
    @patch('muggle.infra.registry.model.init_chat_model')
    def test_get_response_interface(self, mock_init_model):
        # Setup mock registries
        model_registry = ModelRegistry()
        model_registry.register(
            STR_LLM_DEFAULT,
            provider="test-provider",
            model_id="test-model",
            temperature=0.5
        )

        prompt_registry = MagicMock(spec=PromptRegistry)
        prompt_registry.get_system_prompt.return_value = "System Prompt"

        # Setup mock model
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Mocked Response")
        mock_init_model.return_value = mock_model

        # Test
        processor = ChatProcessor(registry=model_registry, prompt_registry=prompt_registry)
        processor.warm_up()
        response = processor.get_response("Hello")

        self.assertEqual(response, "Mocked Response")
        mock_init_model.assert_called_once_with(
            model="test-model",
            model_provider="test-provider",
            temperature=0.5
        )

        # Verify prompt injection
        prompt_registry.get_system_prompt.assert_called_once_with(STR_PROMPT_DEFAULT)
        mock_model.invoke.assert_called_once_with([
            ("system", "System Prompt"),
            ("human", "Hello")
        ])

        self.assertTrue(processor.is_initialized())


from muggle.experimental.graph_processor import GraphProcessor
from langchain_core.messages import AIMessage, HumanMessage

class TestGraphProcessor(unittest.TestCase):
    @patch('muggle.infra.registry.model.init_chat_model')
    @patch('muggle.experimental.graph_processor.create_agent')
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
            "structured_response": {"pass_intent_check": True, "response": "Response 1"},
            "messages": [AIMessage(content="Response 1")]
        }
        
        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry)
        processor.warm_up()
        
        resp1 = processor.get_response("Turn 1", thread_id="t1")
        self.assertEqual(resp1, "Response 1")
        
        # Verify first invocation had 1 message (the human input)
        first_call_state = mock_agent_instance.invoke.call_args_list[0][0][0]
        self.assertEqual(len(first_call_state.messages), 1)
        
        # Turn 2
        mock_agent_instance.invoke.return_value = {
            "structured_response": {"pass_intent_check": True, "response": "Response 2"},
            "messages": [AIMessage(content="Response 2")]
        }
        
        resp2 = processor.get_response("Turn 2", thread_id="t1")
        self.assertEqual(resp2, "Response 2")
        
        # Verify TURN 2 invocation has HISTORY (should be 3 messages now: H1, A1, H2)
        # Note: Depending on how intent-check vs inquiry nodes run, it might be more.
        # But crucially, it should be > 1.
        last_call_state = mock_agent_instance.invoke.call_args_list[-1][0][0]
        self.assertGreater(len(last_call_state.messages), 1)
        
        # Check if Turn 1 message is in Turn 2's state
        contents = [m.content for m in last_call_state.messages]
        self.assertIn("Turn 1", contents)
        self.assertIn("Response 1", contents)
        self.assertIn("Turn 2", contents)

if __name__ == '__main__':
    unittest.main()
