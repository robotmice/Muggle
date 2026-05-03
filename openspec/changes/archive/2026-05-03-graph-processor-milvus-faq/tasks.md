## 1. Infrastructure and State Preparation

- [x] 1.1 Update \`WorkflowState\` in \`src/muggle/core/graph_processor.py\` to include \`vector_store_query: str\` and \`context: list\`
- [x] 1.2 Update \`GraphProcessor.__init__\` to accept and store \`VectorStoreManager\`
- [x] 1.3 Add \`top_k\` to \`config.toml\` under \`[vector_store]\`
- [x] 1.4 Update \`ConfigManager.get_vector_store_params\` in \`src/muggle/infra/config.py\` to support \`top_k\`
- [x] 1.5 Update \`VectorStoreManager.__init__\` to load \`top_k\` from config

## 2. Graph Node Implementation

- [x] 2.1 Implement \`query_rewrite_node\` using \`prompt-query-rewrite.md\`
- [x] 2.2 Implement \`retrieval_node\` to perform Milvus search and populate \`context\`
- [x] 2.3 Refactor \`inquiry_node\` to consume \`context\` from state and render prompt via Jinja2
- [x] 2.4 Update \`StateGraph\` definition to include new nodes and edges (IC -> QR -> RT -> IN)

## 3. Prompt Engineering

- [x] 3.1 Create \`src/muggle/infra/prompts/system/prompt-query-rewrite.md\`
- [x] 3.2 Update \`src/muggle/infra/prompts/system/prompt-inquiry.md\` with Jinja2 \`{{ context }}\` placeholder
- [x] 3.3 Add new constants for the rewrite node and prompt in \`src/muggle/shared/constants.py\`

## 4. Verification and Testing

- [x] 4.1 Create a test script to verify the multi-node RAG flow (Rewrite -> Retrieve -> Inquire)
- [x] 4.2 Verify conversational continuity: ensure follow-up questions result in correct query rewriting
- [x] 4.3 Verify grounding: ensure the final answer is based on retrieved FAQ context
