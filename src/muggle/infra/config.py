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

    def get_llm_params(self) -> dict:
        """Retrieve LLM model parameters from the config file."""
        llm_config = self.config.get("llm", {})
        return {
            "model": llm_config.get("model", "deepseek-chat"),
            "provider": llm_config.get("provider", "deepseek"),
            "temperature": llm_config.get("temperature", 0.7),
        }

    def get_server_params(self) -> dict:
        """Retrieve server settings from the config file."""
        server_config = self.config.get("server", {})
        return {
            "host": server_config.get("host", "127.0.0.1"),
            "port": server_config.get("port", 5000),
            "debug": server_config.get("debug", False),
        }

    def get_prompts_params(self) -> dict:
        """Retrieve prompt registry settings from the config file."""
        prompts_config = self.config.get("prompts", {})
        return {
            "path": prompts_config.get("path", "prompts"),
        }

# Global instance for easy access
cfg = ConfigManager()
