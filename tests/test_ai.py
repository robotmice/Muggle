import unittest
from unittest.mock import MagicMock, patch
from muggle.ai import ChatProcessor
from muggle.registry import ModelRegistry

class TestChatProcessor(unittest.TestCase):
    @patch('muggle.registry.init_chat_model')
    @patch('muggle.ai.cfg')
    def test_get_response_interface(self, mock_cfg, mock_init_model):
        # Setup mock registry
        registry = ModelRegistry()
        registry.register(
            "default", 
            provider="test-provider", 
            model_id="test-model", 
            temperature=0.5
        )
        
        # Setup mock model
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Mocked Response")
        mock_init_model.return_value = mock_model
        
        # Test
        processor = ChatProcessor(registry=registry)
        processor.warm_up()
        response = processor.get_response("Hello")
        
        self.assertEqual(response, "Mocked Response")
        mock_init_model.assert_called_once_with(
            model="test-model",
            model_provider="test-provider",
            temperature=0.5
        )
        mock_model.invoke.assert_called_once_with("Hello")
        self.assertTrue(processor.is_initialized())

if __name__ == '__main__':
    unittest.main()
