# Project Overview: muggle

`muggle` is a Python-based AI application project managed by Poetry. It is designed around a "spec-driven" development workflow called **OpenSpec**, which leverages Gemini CLI for guided exploration, planning, and implementation.

The project uses a modern AI stack, including LangChain, LangGraph, and specialized LLM integrations (DeepSeek, DashScope), along with Milvus for vector storage and Flask for potential web interfaces.

## Project Structure

- `src/muggle/`: Main package for the application logic (layered architecture).
    - `core/`: Pure AI logic and business rules.
    - `infra/`: Infrastructure concerns (Config, Registries, Prompts).
    - `api/`: Web/API layer (Flask, Blueprints, Static assets).
    - `shared/`: Cross-cutting utilities.
- `openspec/`: Contains the configuration (`config.yaml`) and artifacts for the spec-driven development process.
    - `changes/`: Active change containers (Proposal, Specs, Design, Tasks).
    - `specs/`: Project-wide specifications.
- `.gemini/`: Custom Gemini CLI extensions.
    - `commands/opsx/`: Custom command definitions for the OpenSpec workflow.
    - `skills/`: Specialized skills implementing the OpenSpec logic.
- `tests/`: Unit and integration tests.

## Development Workflow: OpenSpec

This project follows the OpenSpec workflow. All significant changes should be managed as "changes" within the `openspec/` directory.

### Core Workflow Commands (Gemini CLI)

Use these commands (via `/opsx:<command>`) to manage the development lifecycle:

| Command | Description |
| :--- | :--- |
| `/opsx:onboard` | Guided onboarding to the OpenSpec workflow. |
| `/opsx:explore` | Investigate and think through problems before starting a change. |
| `/opsx:propose` | Create a new change and generate all artifacts (Proposal, Specs, Design, Tasks). |
| `/opsx:new` | Start a new change, stepping through artifacts one at a time. |
| `/opsx:apply` | Implement the tasks defined in a change's `tasks.md`. |
| `/opsx:verify` | Verify the implementation against the specs and design. |
| `/opsx:archive` | Move a completed change to the archive. |
| `/opsx:continue` | Resume work on an existing change. |
| `/opsx:ff` | Fast-forward: create all artifacts for a change in one step. |

### Artifact Definitions

- **Proposal (`proposal.md`):** Why the change is being made and what it involves.
- **Specs (`specs/`):** Precise, testable requirements in WHEN/THEN/AND format.
- **Design (`design.md`):** How the change will be built (decisions, tradeoffs).
- **Tasks (`tasks.md`):** Implementation checklist.

## Building and Running

### Prerequisites
- Python >= 3.11
- Poetry

### Commands

- **Install Dependencies:** `poetry install`
- **Run Application:** `poetry run muggle`
- **Run Tests:** `poetry run pytest`

## Tech Stack

- **Orchestration:** LangChain, LangGraph
- **Vector DB:** Pymilvus
- **Evaluation:** Ragas
- **Web Framework:** Flask
- **Data Handling:** Pandas, Pydantic
- **Environment:** python-dotenv
