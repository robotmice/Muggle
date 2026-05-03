from pprint import pprint
from typing import Annotated, Sequence

import pydash
from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import StreamMode
from langmem.short_term import SummarizationNode
from pydantic import BaseModel, Field

from muggle.core import ProcessorInterface
from muggle.infra.config import cfg
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import STR_PROMPT_INTENT_CHECK, STR_LLM_DEFAULT, STR_NODE_INTENT_CHECK, STR_NODE_UNHANDLED, STR_PROMPT_INQUIRY, STR_NODE_INQUIRY, \
    STR_NODE_QUERY_REWRITE, STR_PROMPT_QUERY_REWRITE, STR_NODE_RETRIEVAL, STR_NODE_SUMMARIZE


class WorkflowState(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    pass_intent_check: bool = Field(False)
    vector_store_query: str | None = Field(None, description="Rewritten query for vector store")
    retrieved_context: list[dict] = Field(default_factory=list, description="Retrieved context from vector store")
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

        rerank_params = cfg.get_rerank_params()
        # Using dashscope reranker, note it requires DASHSCOPE_API_KEY environment variable.
        self.reranker = DashScopeRerank(top_n=rerank_params["top_n"])
        self.relevance_threshold = rerank_params["relevance_threshold"]
        self.recall_limit = rerank_params["recall_limit"]

        memory_params = cfg.get_memory_params()

        self._ready = False
        self._last_error = None

        def intent_check_node(state: WorkflowState):
            model = registry.get_model(default_model)
            system_prompt = prompt_registry.get_system_prompt(STR_PROMPT_INTENT_CHECK)

            messages = [SystemMessage(content=system_prompt)] + state.messages
            result = model.with_structured_output(IntentCheckResult).invoke(messages)

            return {"pass_intent_check": result.pass_intent_check}

        def inquiry_node(state: WorkflowState):
            # Format context for the prompt
            context_str = ""
            if state.retrieved_context:
                context_str = "\n\n".join([f"### {d['header']}\n{d['text']}" for d in state.retrieved_context])

            model = registry.get_model(default_model)
            system_prompt = prompt_registry.get_system_prompt(STR_PROMPT_INQUIRY, variables={"context": context_str})

            messages = [SystemMessage(content=system_prompt)] + state.messages
            result = model.with_structured_output(InquiryResult).invoke(messages)

            if not result.response:
                pprint(result)

            return {"response": result.response, "messages": [AIMessage(content=result.response or "")]}

        def query_rewrite_node(state: WorkflowState):
            model = registry.get_model(default_model)
            system_prompt = prompt_registry.get_system_prompt(STR_PROMPT_QUERY_REWRITE)

            messages = [SystemMessage(content=system_prompt)] + state.messages
            result = model.with_structured_output(QueryRewriteResult).invoke(messages)

            return {"vector_store_query": result.vector_store_query}

        def retrieval_node(state: WorkflowState):
            query = state.vector_store_query
            if not query:
                return {"context": []}

            # 1. Increase recall for reranking
            results = self.vector_store.search(query_text=query, vector_field="content_vector", limit=self.recall_limit)
            results += (self.vector_store.search(query_text=query, vector_field="header_vector", limit=self.recall_limit))
            if not results:
                return {"context": []}

            # 2. Convert to LangChain Document objects
            docs = [
                Document(
                    page_content=res.get("text", ""),
                    metadata={"header": res.get("header", ""), "is_segment": res.get("is_segment", False)}
                )
                for res in results
            ]

            # 3. Rerank documents
            reranked_docs = self.reranker.compress_documents(documents=docs, query=query)

            # 4. Filter by threshold and convert back to original dict format
            final_context = []
            for doc in reranked_docs:
                # DashScopeRerank injects relevance_score into metadata
                score = doc.metadata.get("relevance_score", 0.0)
                if score >= self.relevance_threshold:
                    final_context.append({
                        "text": doc.page_content,
                        "header": doc.metadata.get("header", ""),
                        "is_segment": doc.metadata.get("is_segment", False),
                        "relevance_score": score
                    })

            return {"retrieved_context": final_context}

        # Initialize the summarization node
        summarizer_node = SummarizationNode(model=self.registry.get_model(self.default_model),
                                            max_tokens=memory_params["max_tokens"],
                                            max_tokens_before_summary=memory_params["max_tokens_before_summary"],
                                            max_summary_tokens=memory_params["max_summary_tokens"],
                                            input_messages_key="messages",
                                            output_messages_key="messages")

        graph_builder = StateGraph(WorkflowState)
        graph_builder.add_node(STR_NODE_INTENT_CHECK, intent_check_node)
        graph_builder.add_node(STR_NODE_QUERY_REWRITE, query_rewrite_node)
        graph_builder.add_node(STR_NODE_RETRIEVAL, retrieval_node)
        graph_builder.add_node(STR_NODE_INQUIRY, inquiry_node)
        graph_builder.add_node(STR_NODE_UNHANDLED, unhandled_response_node)
        graph_builder.add_node(STR_NODE_SUMMARIZE, summarizer_node)

        graph_builder.add_edge(START, STR_NODE_INTENT_CHECK)

        graph_builder.add_conditional_edges(STR_NODE_INTENT_CHECK, ingest_router, {True: STR_NODE_SUMMARIZE, False: STR_NODE_UNHANDLED})
        graph_builder.add_edge(STR_NODE_SUMMARIZE, STR_NODE_QUERY_REWRITE)
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
