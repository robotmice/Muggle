from abc import ABC, abstractmethod
from langchain.chat_models import init_chat_model
from muggle.config import cfg

class ProcessorInterface(ABC):
    @abstractmethod
    def get_response(self, message: str) -> str:
        """Process a message and return a response."""
        pass

class ChatProcessor(ProcessorInterface):
    def __init__(self):
        # Initializing model using parameters from ConfigManager and init_chat_model
        params = cfg.get_ai_params()
        self.model = init_chat_model(
            model=params["model"],
            model_provider=params["provider"],
            temperature=params["temperature"],
        )

    def get_response(self, message: str) -> str:
        try:
            response = self.model.invoke(message)
            return response.content
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"
