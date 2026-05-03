from abc import ABC, abstractmethod


class ProcessorInterface(ABC):
    @abstractmethod
    def get_response(self, message: str, thread_id: str | None = None) -> str:
        """Process a message and return a response."""
        pass
