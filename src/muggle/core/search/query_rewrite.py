from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from muggle.core.state import WorkflowState
from muggle.infra.registry import PromptRegistry
from muggle.shared.constants import STR_PROMPT_QUERY_REWRITE


class QueryRewriteResult(BaseModel):
    query_zh: str = Field(..., description="The rewritten query for zh-CN vector search")
    query_en: str = Field(..., description="The rewritten query for en-US vector search")


class QueryRewriteNode:
    def __init__(self, model, prompt_registry: PromptRegistry):
        self.model = model
        self.prompt_registry = prompt_registry

    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        system_prompt = self.prompt_registry.get_system_prompt(STR_PROMPT_QUERY_REWRITE)
        messages = [SystemMessage(content=system_prompt)] + state.messages
        result = self.model.with_structured_output(QueryRewriteResult).invoke(messages)
        return {"vector_store_queries": {"zh-CN": result.query_zh, "en-US": result.query_en}}
