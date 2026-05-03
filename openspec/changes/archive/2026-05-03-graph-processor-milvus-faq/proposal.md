## Why

The current `GraphProcessor`'s `inquiry_node` relies solely on the LLM's internal knowledge to answer user queries. To provide accurate and project-specific information, it needs to retrieve relevant context from the FAQ stored in Milvus.

## What Changes

- Modify \`GraphProcessor\` to accept a \`VectorStoreManager\` instance in its constructor.
- Introduce a **Query Rewrite** node to analyze conversation history and generate an optimized search query.
- Introduce a **Retrieval** node to perform similarity search in Milvus and store results in the state.
- Update \`inquiry_node\` to consume retrieved context from the state and generate a grounded response.
- Update the \`prompt-inquiry\` to include a placeholder for retrieved FAQ context.

## Capabilities

### New Capabilities
- \`faq-retrieval\`: Capability to retrieve relevant FAQ sections from Milvus based on user inquiry.
- \`query-expansion\`: Capability to rewrite and optimize user queries for vector search based on context.

### Modified Capabilities
- \`llm-processor\`: Update the core processing logic to incorporate a multi-node RAG pipeline (Rewrite -> Retrieve -> Inquire).
- \`ai-processor\`: (Legacy) Tracked for compatibility.

## Impact

- \`src/muggle/core/graph_processor.py\`: Significant refactoring of the LangGraph workflow.
- \`src/muggle/infra/registry/vector.py\`: Used by the new \`retrieval\` node.
- \`src/muggle/infra/prompts/system/\`: New \`prompt-query-rewrite.md\` and updated \`prompt-inquiry.md\`.
- \`src/muggle/shared/constants.py\`: New node and prompt constants.
