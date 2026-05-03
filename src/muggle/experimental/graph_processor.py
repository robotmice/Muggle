from typing import Annotated, Sequence

import pydash
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import StreamMode
from pydantic import BaseModel, Field

from muggle.core.processor import ProcessorInterface
from muggle.infra.registry import ModelRegistry, PromptRegistry
from muggle.shared.constants import STR_PROMPT_INGEST, STR_PROMPT_VALIDATE, STR_LLM_DEFAULT


class WorkflowState(BaseModel):
    messages: Annotated[list, add_messages, Field(default_factory=list)]
    type: str | None = None


def simple_human_message(messages: list[str]):
    return {"messages": [HumanMessage(content=msg) for msg in messages]} if messages else {}


def config_map(thread_id: str | None = None) -> RunnableConfig:
    return RunnableConfig(
        configurable={
            "thread_id": thread_id if thread_id else "NA"
        }
    )


def unhandled_response_node(state: WorkflowState):
    _ = state
    return simple_human_message(["I cannot answer this question."])


class GraphProcessor(ProcessorInterface):
    def __init__(self, registry: ModelRegistry, prompt_registry: PromptRegistry, model_alias: str = STR_LLM_DEFAULT):
        self.registry = registry
        self.prompt_registry = prompt_registry
        self.model_alias = model_alias
        self._ready = False
        self._last_error = None

        self.agent1 = create_agent(model=registry.get_model(model_alias), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_INGEST))
        self.agent2 = create_agent(model=registry.get_model(model_alias), system_prompt=prompt_registry.get_system_prompt(model_alias))
        self.agent3 = create_agent(model=registry.get_model(model_alias), system_prompt=prompt_registry.get_system_prompt(model_alias))
        self.agent4 = create_agent(model=registry.get_model(model_alias), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_VALIDATE))

        graph_builder = StateGraph(WorkflowState)
        self.workflow = graph_builder.compile(checkpointer=InMemorySaver())

    def get_response(self, message: str, thread_id: str | None = None, stream_mode: StreamMode | Sequence[StreamMode] | None = None) -> str:
        last_msg = None
        for chunk in self.workflow.stream(simple_human_message([message]), config=config_map(thread_id), stream_mode=stream_mode):
            print(chunk)
            if isinstance(chunk, AIMessage | ToolMessage):
                last_msg = chunk
            if self._last_error is None:
                self._last_error = chunk
        return pydash.get(last_msg, "content", "")
