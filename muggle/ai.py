import os
from abc import ABC, abstractmethod
from langchain_deepseek import ChatDeepSeek

class ProcessorInterface(ABC):
    @abstractmethod
    def get_response(self, message: str) -> str:
        """Process a message and return a response."""
        pass

class ChatProcessor(ProcessorInterface):
    def __init__(self):
        # Initializing DeepSeek with standard environment variable lookup
        self.model = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.7,
        )

    def get_response(self, message: str) -> str:
        try:
            response = self.model.invoke(message)
            return response.content
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"
