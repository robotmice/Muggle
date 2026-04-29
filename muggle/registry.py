from pathlib import Path
import jinja2
from langchain.chat_models import init_chat_model
from muggle.utils import parse_frontmatter

class ModelRegistry:
    def __init__(self):
        self._definitions = {}
        self._instances = {}

    def register(self, alias: str, provider: str, model_id: str, **kwargs):
        """Register a model definition."""
        self._definitions[alias] = {
            "provider": provider,
            "model_id": model_id,
            "kwargs": kwargs
        }

    def get_model(self, alias: str):
        """Retrieve a model instance, creating it if it doesn't exist (lazy loading)."""
        if alias not in self._instances:
            if alias not in self._definitions:
                raise ValueError(f"Model alias '{alias}' is not registered.")
            
            defn = self._definitions[alias]
            self._instances[alias] = init_chat_model(
                model=defn["model_id"],
                model_provider=defn["provider"],
                **defn["kwargs"]
            )
        
        return self._instances[alias]

    def is_registered(self, alias: str) -> bool:
        return alias in self._definitions

    def clear(self):
        """Clear all instances and definitions (mainly for testing)."""
        self._definitions.clear()
        self._instances.clear()

class PromptRegistry:
    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)
        self._cache = {}  # { (type, name): {metadata, template} }
        self._jinja_env = jinja2.Environment()

    def _get_prompt_path(self, prompt_type: str, prompt_name: str) -> Path:
        return self.prompts_dir / prompt_type / f"{prompt_name}.md"

    def _load_prompt(self, prompt_type: str, prompt_name: str) -> dict:
        cache_key = (prompt_type, prompt_name)
        if cache_key not in self._cache:
            path = self._get_prompt_path(prompt_type, prompt_name)
            if not path.exists():
                raise FileNotFoundError(f"Prompt '{prompt_name}' of type '{prompt_type}' not found at {path}")
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            metadata, template_str = parse_frontmatter(content)
            self._cache[cache_key] = {
                "metadata": metadata,
                "template": self._jinja_env.from_string(template_str)
            }
        
        return self._cache[cache_key]

    def get_system_prompt(self, prompt_name: str, variables: dict = None) -> str:
        """Retrieve and render a system prompt."""
        prompt_data = self._load_prompt("system", prompt_name)
        return prompt_data["template"].render(**(variables or {}))

    def get_user_prompt(self, prompt_name: str, variables: dict = None) -> str:
        """Retrieve and render a user prompt."""
        prompt_data = self._load_prompt("user", prompt_name)
        return prompt_data["template"].render(**(variables or {}))
