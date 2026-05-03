from typing import Annotated, Sequence

import pydash
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import StreamMode
from pydantic import BaseModel, Field

from muggle.core.processor import ProcessorInterface
from muggle.infra.registry import ModelRegistry, PromptRegistry
from muggle.shared.constants import STR_PROMPT_INGEST, STR_LLM_DEFAULT, STR_NODE_INGEST, STR_PROMPT_DEFAULT


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
    def __init__(self, registry: ModelRegistry, prompt_registry: PromptRegistry, default_model: str = STR_LLM_DEFAULT):
        self.registry = registry
        self.prompt_registry = prompt_registry
        self.default_model = default_model
        self._ready = False
        self._last_error = None

        self.agent_ingest = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_INGEST))
        self.agent2 = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_DEFAULT))
        self.agent3 = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_DEFAULT))
        self.agent4 = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_DEFAULT))

        graph_builder = StateGraph(WorkflowState)
        graph_builder.add_node(STR_NODE_INGEST, self.agent_ingest)
        graph_builder.add_edge(START, STR_NODE_INGEST)
        graph_builder.add_edge(STR_NODE_INGEST, END)
        self.workflow = graph_builder.compile(checkpointer=InMemorySaver())

    def get_response(self, message: str, thread_id: str | None = None, stream_mode: StreamMode | Sequence[StreamMode] | None = None) -> str:
        for chunk in self.workflow.stream(simple_human_message([message]), config=config_map(thread_id), stream_mode=stream_mode):
            print(chunk)
            if self._last_error is None:
                self._last_error = chunk
        state = self.workflow.get_state(config=config_map())
        return pydash.get(state, "values.messages[-1].content", "")

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

    def is_initialized(self) -> bool:
        """Check if the processor is warmed up and ready."""
        return self._ready

    @property
    def last_error(self):
        return self._last_error
