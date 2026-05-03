import logging
from abc import ABC, abstractmethod

from muggle.core.exceptions import PromptNotFoundError
from muggle.infra.registry import ModelRegistry, PromptRegistry
from muggle.shared.constants import STR_LLM_DEFAULT, STR_PROMPT_DEFAULT

logger = logging.getLogger(__name__)


class ProcessorInterface(ABC):
    @abstractmethod
    def get_response(self, message: str) -> str:
        """Process a message and return a response."""
        pass


class ChatProcessor(ProcessorInterface):
    def __init__(self, registry: ModelRegistry, prompt_registry: PromptRegistry, default_model: str = STR_LLM_DEFAULT):
        self.registry = registry
        self.prompt_registry = prompt_registry
        self.default_model = default_model
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
            if not self.registry.is_registered(self.default_model):
                raise ValueError(f"Model '{self.default_model}' is not registered in the ModelRegistry.")

            # Trigger lazy loading/instantiation
            self.registry.get_model(self.default_model)

            self._ready = True
            self._last_error = None
        except Exception as e:
            self._ready = False
            self._last_error = str(e)
            raise e

    def get_response(self, message: str) -> str:
        try:
            model = self.registry.get_model(self.default_model)

            try:
                system_prompt = self.prompt_registry.get_system_prompt(STR_PROMPT_DEFAULT)
            except PromptNotFoundError as e:
                logger.error(f"Required prompt missing: {e}")
                return "Error: LLM configuration incomplete (system prompt missing)."

            messages = [
                ("system", system_prompt),
                ("human", message)
            ]

            response = model.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"
