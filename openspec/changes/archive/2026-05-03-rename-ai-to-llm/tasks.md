## 1. Infrastructure Renaming

- [x] 1.1 Update `config.toml` to use `[llm]` section instead of `[ai]`
- [x] 1.2 Update `src/muggle/infra/config.py` to use `llm` keys and rename `ai_config` to `llm_config`
- [x] 1.3 Update `.env.example` if it contains any `AI_*` variables

## 2. Core and API Renaming

- [x] 2.1 Rename `AI Processor` to `LLM Processor` in `src/muggle/blueprints/chat.py` and error messages
- [x] 2.2 Update `src/muggle/core/processor.py` to use `LLM` terminology in log messages and internal variables
- [x] 2.3 Verify all occurrences of `ai` (as a whole word) are replaced with `llm` where appropriate

## 3. Frontend Renaming

- [x] 3.1 Update `src/muggle/static/index.html` to rename CSS class `.ai` to `.llm`
- [x] 3.2 Update JavaScript in `index.html` to use `llm` for message types

## 4. Documentation Updates

- [x] 4.1 Update `README.md` to use `LLM` instead of `AI`
- [x] 4.2 Update `GEMINI.md` to reflect naming changes
- [x] 4.3 Update all existing spec files in `openspec/specs/` to use precise terminology

## 5. Verification and Cleanup

- [x] 4.1 Run `poetry run pytest` to ensure no regressions
- [x] 4.2 Manually verify the chat interface still works and uses the new terminology
- [x] 4.3 Remove `openspec/specs/ai-processor` after the change is archived (or as part of sync)
