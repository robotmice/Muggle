import os
import tomllib
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        # Load environment variables from .env
        load_dotenv()
        
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        
        with open(self.config_path, "rb") as f:
            return tomllib.load(f)

    def get_ai_params(self) -> dict:
        """Retrieve AI model parameters from the config file."""
        ai_config = self.config.get("ai", {})
        return {
            "model": ai_config.get("model", "deepseek-chat"),
            "provider": ai_config.get("provider", "deepseek"),
            "temperature": ai_config.get("temperature", 0.7),
        }

    def get_server_params(self) -> dict:
        """Retrieve server settings from the config file."""
        server_config = self.config.get("server", {})
        return {
            "host": server_config.get("host", "127.0.0.1"),
            "port": server_config.get("port", 5000),
            "debug": server_config.get("debug", False),
        }

# Global instance for easy access
cfg = ConfigManager()
