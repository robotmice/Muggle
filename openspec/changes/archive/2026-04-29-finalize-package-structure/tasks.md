# Tasks: Finalize Package Structure

## 1. Create Package Markers
- [x] 1.1 Create `src/muggle/core/__init__.py`
- [x] 1.2 Create `src/muggle/infra/__init__.py`
- [x] 1.3 Create `src/muggle/infra/prompts/__init__.py`
- [x] 1.4 Create `src/muggle/infra/prompts/system/__init__.py`
- [x] 1.5 Create `src/muggle/infra/prompts/user/__init__.py`
- [x] 1.6 Create `src/muggle/shared/__init__.py`

## 2. Validation
- [x] 2.1 Verify application startup (`poetry run muggle`)
- [x] 2.2 Verify resource loading (ensure `PromptRegistry` can still load prompts)
- [x] 2.3 Run full test suite (`poetry run pytest`)
