from pprint import pprint
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
from muggle.shared.constants import STR_PROMPT_INGEST, STR_LLM_DEFAULT, STR_NODE_INGEST, STR_NODE_UNHANDLED, STR_PROMPT_INSURANCE, STR_NODE_INSURANCE


class WorkflowState(BaseModel):
    messages: Annotated[list, add_messages, Field(default_factory=list)]
    type: Annotated[str | None, Field(description="")] = None
    response: Annotated[str | None, Field(description="Response of the inquiry")] = None


class IngestResult(BaseModel):
    type: Annotated[str | None, Field(description="Result of the analysis")] = None


class InsuranceInquiryResult(BaseModel):
    response: Annotated[str | None, Field(description="Response of the inquiry")] = None


def simple_human_message(messages: list[str]):
    return {"messages": [HumanMessage(content=msg) for msg in messages]} if messages else {}


def config_map(thread_id: str | None = None) -> RunnableConfig:
    return RunnableConfig(
        configurable={
            "thread_id": thread_id if thread_id else "NA"
        }
    )


def ingest_router(state: WorkflowState) -> str:
    if state.type == "insurance":
        return STR_NODE_INSURANCE
    else:
        return STR_NODE_UNHANDLED


def unhandled_response_node(state: WorkflowState):
    _ = state
    return {"response": "I cannot respond to this question."}


class GraphProcessor(ProcessorInterface):
    def __init__(self, registry: ModelRegistry, prompt_registry: PromptRegistry, default_model: str = STR_LLM_DEFAULT):
        self.registry = registry
        self.prompt_registry = prompt_registry
        self.default_model = default_model
        self._ready = False
        self._last_error = None

        def ingest_node(state: WorkflowState):
            state = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_INGEST),
                                 response_format=IngestResult).invoke(state)

            return {"type": pydash.get(state, "structured_response.type"),
                    "messages": pydash.get(state, "messages")}

        def insurance_inquiry_node(state: WorkflowState):
            state = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_INSURANCE),
                                 response_format=InsuranceInquiryResult).invoke(state)

            return {"response": pydash.get(state, "structured_response.response"),
                    "messages": pydash.get(state, "messages")}

        graph_builder = StateGraph(WorkflowState)
        graph_builder.add_node(STR_NODE_INGEST, ingest_node)
        graph_builder.add_node(STR_NODE_INSURANCE, insurance_inquiry_node)
        graph_builder.add_node(STR_NODE_UNHANDLED, unhandled_response_node)

        graph_builder.add_edge(START, STR_NODE_INGEST)

        graph_builder.add_conditional_edges(STR_NODE_INGEST, ingest_router, [STR_NODE_INSURANCE, STR_NODE_UNHANDLED])

        graph_builder.add_edge(STR_NODE_INSURANCE, END)
        graph_builder.add_edge(STR_NODE_UNHANDLED, END)

        self.workflow = graph_builder.compile(checkpointer=InMemorySaver())
        self.workflow.get_graph().print_ascii()

    def get_response(self, message: str, thread_id: str | None = None, stream_mode: StreamMode | Sequence[StreamMode] | None = None) -> str:
        for chunk in self.workflow.stream(simple_human_message([message]), config=config_map(thread_id), stream_mode=stream_mode):
            pprint(chunk)

        state = self.workflow.get_state(config=config_map(thread_id))
        return pydash.get(state.values, "response", "")

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
