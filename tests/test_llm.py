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


if __name__ == '__main__':
    unittest.main()
