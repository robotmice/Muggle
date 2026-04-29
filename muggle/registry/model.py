from langchain.chat_models import init_chat_model

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
