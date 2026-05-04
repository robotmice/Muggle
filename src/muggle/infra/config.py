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

    def get_vector_store_params(self) -> dict:
        """Retrieve vector store settings from config and environment."""
        vs_config = self.config.get("vector_store", {})
        return {
            "collection_name": vs_config.get("collection_name", "muggle_vectors"),
            "embedding_model": vs_config.get("embedding_model", "text-embedding-v3"),
            "top_k": vs_config.get("top_k", 3),
            "uri": os.getenv("MILVUS_URI"),
            "token": os.getenv("MILVUS_TOKEN"),
        }

    def get_rerank_params(self) -> dict:
        """Retrieve rerank settings from the config file."""
        rerank_config = self.config.get("rerank", {})
        return {
            "top_n": rerank_config.get("top_n", 3),
            "relevance_threshold": rerank_config.get("relevance_threshold", 0.1),
            "recall_limit": rerank_config.get("recall_limit", 15),
        }

    def get_memory_params(self) -> dict:
        """Retrieve memory settings from the config file."""
        memory_config = self.config.get("memory", {})
        return {
            "max_tokens": memory_config.get("max_tokens", 1024),
            "max_tokens_before_summary": memory_config.get("max_tokens_before_summary", 4096),
            "max_summary_tokens": memory_config.get("max_summary_tokens", 256),
        }

    def get_validate_params(self) -> dict:
        """Retrieve validation settings from the config file."""
        validate_config = self.config.get("validate", {})
        return {
            "threshold": validate_config.get("threshold", 0.8),
            "max_attempts": validate_config.get("max_attempts", 5),
        }

    def get_hybrid_search_params(self) -> dict:
        """Retrieve hybrid search settings from the config file."""
        hs_config = self.config.get("hybrid_search", {})
        return {
            "rrf_k": hs_config.get("rrf_k", 60),
            "recall_limit_per_route": hs_config.get("recall_limit_per_route", 15),
        }


# Global instance for easy access
cfg = ConfigManager()
