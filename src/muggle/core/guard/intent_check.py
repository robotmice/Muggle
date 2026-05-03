from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from muggle.core.state import WorkflowState
from muggle.infra.registry import PromptRegistry
from muggle.shared.constants import STR_PROMPT_INTENT_CHECK


class IntentCheckResult(BaseModel):
    pass_intent_check: bool = Field(False, description="Result of the intent analysis")


class IntentCheckNode:
    def __init__(self, model, prompt_registry: PromptRegistry):
        self.model = model
        self.prompt_registry = prompt_registry

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        system_prompt = self.prompt_registry.get_system_prompt(STR_PROMPT_INTENT_CHECK)
        messages = [SystemMessage(content=system_prompt)] + state.messages
        result = self.model.with_structured_output(IntentCheckResult).invoke(messages)
        return {"pass_intent_check": result.pass_intent_check, "retry_count": 0}
