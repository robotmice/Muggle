from typing import Annotated, Sequence

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph.message import add_messages
from langgraph.types import StreamMode
from pydantic import BaseModel, Field

from muggle.shared.constants import STR_NODE_SUMMARIZE, STR_NODE_UNHANDLED


class WorkflowState(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    pass_intent_check: bool = Field(False)
    vector_store_query: str | None = Field(None, description="Rewritten query for vector store")
    retrieved_context: list[dict] = Field(default_factory=list, description="Retrieved context from vector store")
    response: str | None = Field(None, description="Response to the inquiry")
    retry_count: int = Field(0, description="Number of validation retries attempted")
    pass_validation: bool = Field(False, description="Whether the response passed validation")


def ingest_router(state: WorkflowState) -> bool:
    return state.pass_intent_check


def validation_router(state: WorkflowState) -> str:
    if state.pass_validation:
        return END
    if state.retry_count >= 5:
        return STR_NODE_UNHANDLED
    return STR_NODE_SUMMARIZE


def simple_human_message(messages: list[str]):
    return {"messages": [HumanMessage(content=msg) for msg in messages]} if messages else {}


def config_map(thread_id: str | None = None) -> RunnableConfig:
    return RunnableConfig(
        configurable={
            "thread_id": thread_id if thread_id else "NA"
        }
    )
