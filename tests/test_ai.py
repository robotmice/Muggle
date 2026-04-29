import unittest
from unittest.mock import MagicMock, patch
from muggle.ai import ChatProcessor

class TestChatProcessor(unittest.TestCase):
    @patch('muggle.ai.init_chat_model')
    @patch('muggle.ai.cfg')
    def test_get_response_interface(self, mock_cfg, mock_init_model):
        # Setup mock config
        mock_cfg.get_ai_params.return_value = {
            "model": "test-model",
            "provider": "test-provider",
            "temperature": 0.5
        }
        
        # Setup mock model
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Mocked Response")
        mock_init_model.return_value = mock_model
        
        # Test
        processor = ChatProcessor()
        response = processor.get_response("Hello")
        
        self.assertEqual(response, "Mocked Response")
        mock_init_model.assert_called_once_with(
            model="test-model",
            model_provider="test-provider",
            temperature=0.5
        )
        mock_model.invoke.assert_called_once_with("Hello")

if __name__ == '__main__':
    unittest.main()
