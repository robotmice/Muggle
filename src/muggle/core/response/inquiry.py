from pprint import pprint

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from muggle.core.state import WorkflowState
from muggle.infra.registry import PromptRegistry
from muggle.shared.constants import STR_PROMPT_INQUIRY


class InquiryResult(BaseModel):
    response: str | None = Field(None, description="Response to the inquiry")


class InquiryNode:
    def __init__(self, model, prompt_registry: PromptRegistry):
        self.model = model
        self.prompt_registry = prompt_registry

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        context_str = ""
        if state.retrieved_context:
            context_str = "\n\n".join(
                [f"### {d['header']}\n{d['text']}" for d in state.retrieved_context]
            )

        system_prompt = self.prompt_registry.get_system_prompt(
            STR_PROMPT_INQUIRY, variables={"context": context_str}
        )

        messages = [SystemMessage(content=system_prompt)] + state.messages
        result = self.model.with_structured_output(InquiryResult).invoke(messages)

        if not result.response:
            pprint(result)

        return {"response": result.response, "messages": [AIMessage(content=result.response or "")]}
