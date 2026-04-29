from abc import ABC, abstractmethod
from langchain.chat_models import init_chat_model
from muggle.config import cfg
from muggle.registry import ModelRegistry

class ProcessorInterface(ABC):
    @abstractmethod
    def get_response(self, message: str) -> str:
        """Process a message and return a response."""
        pass

class ChatProcessor(ProcessorInterface):
    def __init__(self, registry: ModelRegistry, model_alias: str = "default"):
        self.registry = registry
        self.model_alias = model_alias
        self._ready = False
        self._last_error = None

    def is_initialized(self) -> bool:
        """Check if the processor is warmed up and ready."""
        return self._ready

    @property
    def last_error(self):
        return self._last_error

    def warm_up(self):
        """Perform internal initialization and validation."""
        try:
            if not self.registry.is_registered(self.model_alias):
                raise ValueError(f"Model alias '{self.model_alias}' is not registered in the ModelRegistry.")
            
            # Trigger lazy loading/instantiation
            self.registry.get_model(self.model_alias)
            
            self._ready = True
            self._last_error = None
        except Exception as e:
            self._ready = False
            self._last_error = str(e)
            raise e

    def get_response(self, message: str) -> str:
        try:
            model = self.registry.get_model(self.model_alias)
            response = model.invoke(message)
            return response.content
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"
