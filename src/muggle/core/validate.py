from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from muggle.core.state import WorkflowState
from muggle.infra.registry import PromptRegistry
from muggle.shared.constants import STR_PROMPT_VALIDATE


class ValidationResult(BaseModel):
    pass_validation: bool = Field(False, description="Whether the response passes the quality threshold")
    score: float = Field(0.0, description="Quality score between 0 and 1")
    critical_flaws: list[str] = Field(default_factory=list, description="List of critical flaws found")


class ValidateNode:
    def __init__(self, model, prompt_registry: PromptRegistry, threshold: float = 0.8):
        self.model = model
        self.prompt_registry = prompt_registry
        self.threshold = threshold

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        system_prompt = self.prompt_registry.get_system_prompt(
            STR_PROMPT_VALIDATE, variables={"threshold": str(self.threshold)}
        )
        messages = [SystemMessage(content=system_prompt)] + state.messages
        result = self.model.with_structured_output(ValidationResult).invoke(messages)
        return {
            "pass_validation": result.pass_validation,
            "retry_count": state.retry_count + 1 if not result.pass_validation else state.retry_count,
        }
