from pprint import pprint
from typing import Sequence

import pydash
from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import StreamMode
from langmem.short_term import SummarizationNode

from muggle.core import ProcessorInterface
from muggle.core.guard import IntentCheckNode, FallbackNode
from muggle.core.response import InquiryNode
from muggle.core.search import QueryRewriteNode, RetrievalNode
from muggle.core.state import WorkflowState, ingest_router, ValidationRouter, simple_human_message, config_map
from muggle.core.validation import ValidationNode
from muggle.infra.config import cfg
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import (
    STR_LLM_DEFAULT,
    STR_NODE_INTENT_CHECK, STR_NODE_FALLBACK,
    STR_NODE_INQUIRY, STR_NODE_QUERY_REWRITE,
    STR_NODE_RETRIEVAL, STR_NODE_SUMMARIZATION, STR_NODE_VALIDATION,
)


class GraphProcessor(ProcessorInterface):
    def __init__(self, registry: ModelRegistry, prompt_registry: PromptRegistry,
                 vector_stores: list[VectorStoreManager], default_model: str = STR_LLM_DEFAULT):
        self.registry = registry
        self.prompt_registry = prompt_registry
        self.vector_stores = vector_stores
        self.default_model = default_model

        model = registry.get_model(default_model)

        rerank_params = cfg.get_rerank_params()
        memory_params = cfg.get_memory_params()
        validate_params = cfg.get_validate_params()

        # -- nodes --
        intent_check = IntentCheckNode(model, prompt_registry)
        summarize = SummarizationNode(
            model=model,
            max_tokens=memory_params["max_tokens"],
            max_tokens_before_summary=memory_params["max_tokens_before_summary"],
            max_summary_tokens=memory_params["max_summary_tokens"],
            input_messages_key="messages",
            output_messages_key="messages",
        )
        query_rewrite = QueryRewriteNode(model, prompt_registry)
        retrieval = RetrievalNode(
            vector_stores,
            reranker=DashScopeRerank(top_n=rerank_params["top_n"]),
            recall_limit=rerank_params["recall_limit"],
            relevance_threshold=rerank_params["relevance_threshold"],
        )
        inquiry = InquiryNode(model, prompt_registry)
        validate = ValidationNode(model, prompt_registry, threshold=validate_params["threshold"])
        fallback = FallbackNode()

        # -- graph --
        builder = StateGraph(WorkflowState)
        builder.add_node(STR_NODE_INTENT_CHECK, intent_check)
        builder.add_node(STR_NODE_SUMMARIZATION, summarize)
        builder.add_node(STR_NODE_QUERY_REWRITE, query_rewrite)
        builder.add_node(STR_NODE_RETRIEVAL, retrieval)
        builder.add_node(STR_NODE_INQUIRY, inquiry)
        builder.add_node(STR_NODE_VALIDATION, validate)
        builder.add_node(STR_NODE_FALLBACK, fallback)

        builder.add_edge(START, STR_NODE_INTENT_CHECK)
        builder.add_conditional_edges(STR_NODE_INTENT_CHECK, ingest_router, {
            True: STR_NODE_SUMMARIZATION, False: STR_NODE_FALLBACK
        })
        builder.add_edge(STR_NODE_SUMMARIZATION, STR_NODE_QUERY_REWRITE)
        builder.add_edge(STR_NODE_QUERY_REWRITE, STR_NODE_RETRIEVAL)
        builder.add_edge(STR_NODE_RETRIEVAL, STR_NODE_INQUIRY)
        builder.add_edge(STR_NODE_INQUIRY, STR_NODE_VALIDATION)
        validation_router = ValidationRouter(max_attempts=validate_params["max_attempts"])
        builder.add_conditional_edges(STR_NODE_VALIDATION, validation_router, {
            END: END,
            STR_NODE_FALLBACK: STR_NODE_FALLBACK,
            STR_NODE_SUMMARIZATION: STR_NODE_SUMMARIZATION,
        })
        builder.add_edge(STR_NODE_FALLBACK, END)

        self.workflow = builder.compile(checkpointer=InMemorySaver())
        self.workflow.get_graph().print_ascii()

    def get_response(self, message: str, thread_id: str | None = None,
                     stream_mode: StreamMode | Sequence[StreamMode] | None = None) -> str:
        try:
            for chunk in self.workflow.stream(
                simple_human_message([message]),
                config=config_map(thread_id),
                stream_mode=stream_mode,
            ):
                pprint(chunk)

            state = self.workflow.get_state(config=config_map(thread_id))
            return pydash.get(state.values, "response", "")
        except Exception as e:
            from muggle.core.exceptions import PromptNotFoundError
            if isinstance(e, PromptNotFoundError):
                return "Error: LLM configuration incomplete (required prompt missing)."
            return f"Error connecting to LLM: {str(e)}"

