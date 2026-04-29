import unittest
import os
from unittest.mock import patch, MagicMock
from muggle.config import ConfigManager

class TestConfigManager(unittest.TestCase):
    @patch("muggle.config.load_dotenv")
    @patch("tomllib.load")
    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_default_params(self, mock_exists, mock_open, mock_toml_load, mock_load_dotenv):
        # Setup mocks
        mock_exists.return_value = True
        mock_toml_load.return_value = {
            "ai": {
                "provider": "test-provider",
                "model": "test-model",
                "temperature": 0.5
            }
        }
        
        config = ConfigManager(config_path="dummy.toml")
        params = config.get_ai_params()
        
        self.assertEqual(params["provider"], "test-provider")
        self.assertEqual(params["model"], "test-model")
        self.assertEqual(params["temperature"], 0.5)

    @patch("muggle.config.load_dotenv")
    def test_dotenv_loading(self, mock_load_dotenv):
        ConfigManager()
        mock_load_dotenv.assert_called_once()

if __name__ == '__main__':
    unittest.main()
