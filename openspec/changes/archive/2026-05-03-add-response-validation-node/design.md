## Context

The LangGraph pipeline currently ends with `InquiryNode → END`. The InquiryNode uses structured output to generate a response, but there is no quality gate between generation and delivery to the user. The `prompt-validate.md` system prompt already exists (insurance compliance scoring rubric with weighted criteria and boolean threshold decision), as do the constants `STR_NODE_VALIDATE` and `STR_PROMPT_VALIDATE` in `shared/constants.py`.

## Goals / Non-Goals

**Goals:**
- Add a ValidationNode that scores every Inquiry response before returning it to the user
- Loop back through Summarization → QueryRewrite → Retrieval → Inquiry on validation failure, up to 5 attempts
- Route to UnhandledNode when all 5 retries are exhausted
- Use existing `prompt-validate.md` and existing constants — no new prompt or constant files needed

**Non-Goals:**
- Feedback-based retry (injecting validation critique into the message stream) — blind re-generation only
- Modifying the InquiryNode or its prompt
- Changing the UnhandledNode response text
- Persisting validation scores or building a quality dashboard

## Decisions

### Decision 1: Loop target is Summarization, not START or Inquiry

Looping back to START re-runs IntentCheck, which is non-deterministic and could fail on a previously-passing message. Looping back to Inquiry alone re-generates the response but reuses the same rewritten query and retrieved context — no fresh retrieval. Looping to Summarization re-runs the full pipeline (summarize → rewrite → retrieve → inquire) while keeping the intent decision stable.

**Alternative considered**: Loop back to IntentCheck. Rejected because non-deterministic re-check could derail a valid conversation.

### Decision 2: ValidateNode lives in `core/validate.py` (new response sub-package)

Following the pipeline-stage layout convention (`guard/`, `search/`, `response/`), validation is a distinct stage after response generation. It gets its own sub-package `core/validate.py` (a single module, not a directory package, since there's only one node).

**Alternative considered**: Place ValidateNode in `core/response/` alongside InquiryNode. Rejected because validation is conceptually a separate pipeline stage with its own Pydantic model and routing logic.

### Decision 3: Blind re-generation (no feedback injection)

On validation failure, the retry runs the same nodes with the same state. The LLM's non-determinism (`temperature=0.7`) is the only source of variation. This keeps the implementation simple and avoids modifying node contracts to accept feedback.

**Alternative considered**: Inject validation critique as a synthetic message before the Summarization step. Deferred as future enhancement.

### Decision 4: Counter reset in IntentCheckNode

`IntentCheckNode.__call__` returns `{"retry_count": 0}` so every new user message resets the counter. This avoids the counter persisting across messages via LangGraph checkpointing.

**Alternative considered**: Reset in a dedicated initialization node at START. Rejected because it adds a node solely for field reset.

### Decision 5: Threshold from config, not hardcoded

The `{{ threshold }}` variable in `prompt-validate.md` is rendered by PromptRegistry's Jinja2 environment. The value comes from a new `[validate]` section in `config.toml`, read in `GraphProcessor.__init__` and passed to `ValidateNode.__init__`. This follows the existing pattern (`[rerank]` params → `RetrievalNode`).

## Risks / Trade-offs

- **Latency**: Each validation adds one LLM call. Worst case (5 retries) adds 5 validation calls + 5 re-runs of Summarization/QueryRewrite/Retrieval/Inquiry. The common case (first attempt passes) adds exactly one call. Mitigation: the threshold can be tuned in config.
- **LLM cost**: Same profile as latency — one extra call in the common case. Acceptable given the quality improvement.
- **Non-deterministic retry may not help**: Blind re-generation with no feedback may produce the same failure repeatedly, exhausting all retries. Mitigation: `temperature=0.7` provides some variation; if systematic failures occur, feedback-based retry can be added later.
- **Counter leak via checkpoint**: If `IntentCheckNode` fails to reset `retry_count` (e.g., a code path that skips it), the counter from a previous message could carry over. Mitigation: the default value is 0, and `IntentCheckNode` is always the first node in the pipeline.
