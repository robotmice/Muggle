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

from muggle.core import ProcessorInterface
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import STR_PROMPT_INTENT_CHECK, STR_LLM_DEFAULT, STR_NODE_INTENT_CHECK, STR_NODE_UNHANDLED, STR_PROMPT_INQUIRY, STR_NODE_INQUIRY, STR_NODE_QUERY_REWRITE, STR_PROMPT_QUERY_REWRITE, STR_NODE_RETRIEVAL


class WorkflowState(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    pass_intent_check: bool = Field(False)
    vector_store_query: str | None = Field(None, description="Rewritten query for vector store")
    context: list[dict] = Field(default_factory=list, description="Retrieved context from vector store")
    response: str | None = Field(None, description="Response to the inquiry")


class IntentCheckResult(BaseModel):
    pass_intent_check: bool = Field(False, description="Result of the intent analysis")


class InquiryResult(BaseModel):
    response: str | None = Field(None, description="Response to the inquiry")


class QueryRewriteResult(BaseModel):
    vector_store_query: str = Field(..., description="The rewritten query for vector search")


def simple_human_message(messages: list[str]):
    return {"messages": [HumanMessage(content=msg) for msg in messages]} if messages else {}


def config_map(thread_id: str | None = None) -> RunnableConfig:
    return RunnableConfig(
        configurable={
            "thread_id": thread_id if thread_id else "NA"
        }
    )


def ingest_router(state: WorkflowState) -> bool:
    return state.pass_intent_check


def unhandled_response_node(state: WorkflowState):
    _ = state
    return {"response": "I cannot respond to this question."}


class GraphProcessor(ProcessorInterface):
    def __init__(self, registry: ModelRegistry, prompt_registry: PromptRegistry, vector_store: VectorStoreManager, default_model: str = STR_LLM_DEFAULT):
        self.registry = registry
        self.prompt_registry = prompt_registry
        self.vector_store = vector_store
        self.default_model = default_model
        self._ready = False
        self._last_error = None

        def intent_check_node(state: WorkflowState):
            state = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_INTENT_CHECK),
                                 response_format=IntentCheckResult).invoke(state)

            return {"pass_intent_check": pydash.get(state, "structured_response.pass_intent_check"),
                    "messages": pydash.get(state, "messages")}

        def inquiry_node(state: WorkflowState):
            # Format context for the prompt
            context_str = ""
            if state.context:
                context_str = "\n\n".join([f"### {d['header']}\n{d['text']}" for d in state.context])

            system_prompt = prompt_registry.get_system_prompt(STR_PROMPT_INQUIRY, variables={"context": context_str})
            state = create_agent(model=registry.get_model(default_model), system_prompt=system_prompt,
                                 response_format=InquiryResult).invoke(state)

            return {"response": pydash.get(state, "structured_response.response"),
                    "messages": pydash.get(state, "messages")}

        def query_rewrite_node(state: WorkflowState):
            state = create_agent(model=registry.get_model(default_model), system_prompt=prompt_registry.get_system_prompt(STR_PROMPT_QUERY_REWRITE),
                                 response_format=QueryRewriteResult).invoke(state)

            return {"vector_store_query": pydash.get(state, "structured_response.vector_store_query")}

        def retrieval_node(state: WorkflowState):
            query = state.vector_store_query
            if not query:
                return {"context": []}

            results = self.vector_store.search(query_text=query)
            return {"context": results}

        graph_builder = StateGraph(WorkflowState)
        graph_builder.add_node(STR_NODE_INTENT_CHECK, intent_check_node)
        graph_builder.add_node(STR_NODE_QUERY_REWRITE, query_rewrite_node)
        graph_builder.add_node(STR_NODE_RETRIEVAL, retrieval_node)
        graph_builder.add_node(STR_NODE_INQUIRY, inquiry_node)
        graph_builder.add_node(STR_NODE_UNHANDLED, unhandled_response_node)

        graph_builder.add_edge(START, STR_NODE_INTENT_CHECK)

        graph_builder.add_conditional_edges(STR_NODE_INTENT_CHECK, ingest_router, {True: STR_NODE_QUERY_REWRITE, False: STR_NODE_UNHANDLED})
        graph_builder.add_edge(STR_NODE_QUERY_REWRITE, STR_NODE_RETRIEVAL)
        graph_builder.add_edge(STR_NODE_RETRIEVAL, STR_NODE_INQUIRY)

        graph_builder.add_edge(STR_NODE_INQUIRY, END)
        graph_builder.add_edge(STR_NODE_UNHANDLED, END)

        self.workflow = graph_builder.compile(checkpointer=InMemorySaver())
        self.workflow.get_graph().print_ascii()

    def get_response(self, message: str, thread_id: str | None = None, stream_mode: StreamMode | Sequence[StreamMode] | None = None) -> str:
        try:
            for chunk in self.workflow.stream(simple_human_message([message]), config=config_map(thread_id), stream_mode=stream_mode):
                pprint(chunk)

            state = self.workflow.get_state(config=config_map(thread_id))
            return pydash.get(state.values, "response", "")
        except Exception as e:
            from muggle.core.exceptions import PromptNotFoundError
            if isinstance(e, PromptNotFoundError):
                return "Error: LLM configuration incomplete (required prompt missing)."
            return f"Error connecting to LLM: {str(e)}"

    def warm_up(self):
        """Perform internal initialization and validation."""
        try:
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
