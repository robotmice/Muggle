import unittest
from unittest.mock import MagicMock, patch
from muggle.ai import ChatProcessor

class TestChatProcessor(unittest.TestCase):
    @patch('muggle.ai.ChatDeepSeek')
    def test_get_response_interface(self, mock_chat):
        # Setup mock
        instance = mock_chat.return_value
        instance.invoke.return_value = MagicMock(content="Mocked DeepSeek Response")
        
        # Test
        processor = ChatProcessor()
        response = processor.get_response("Hello")
        
        self.assertEqual(response, "Mocked DeepSeek Response")
        instance.invoke.assert_called_once_with("Hello")

if __name__ == '__main__':
    unittest.main()
