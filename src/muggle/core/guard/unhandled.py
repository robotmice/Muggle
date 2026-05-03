from langchain_core.runnables import RunnableConfig

from muggle.core.state import WorkflowState


class UnhandledNode:
    def __call__(self, state: WorkflowState, config: RunnableConfig) -> dict:
        return {"response": "I cannot respond to this question."}
