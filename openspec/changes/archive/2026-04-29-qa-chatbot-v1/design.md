## Context
The project currently has no functional UI or AI bridge. We need to implement a simple Q&A chatbot that adheres to the project's stack (Poetry, Flask, LangChain) while remaining simple and extensible for future LangGraph state management.

## Goals / Non-Goals

**Goals:**
- Implement a functional chat interface (SPA).
- Create a Flask API to handle chat requests.
- Design a modular AI processor interface that can be easily swapped for LangGraph.

**Non-Goals:**
- Implementing actual LangGraph state machines in this version.
- Persistent user history in a database.
- Complex styling or animations.

## Decisions

### 1. Flask for Backend
**Decision:** Use Flask as the web framework.
**Rationale:** It's lightweight and perfect for simple APIs. It aligns with the project's requirement for a simple backend.
**Alternatives:** FastAPI (considered, but Flask is explicitly mentioned in the project context).

### 2. Vanilla JavaScript for SPA
**Decision:** Use a single `index.html` with embedded CSS and vanilla JS (Fetch API).
**Rationale:** Avoids the complexity of a build system (npm/webpack) for a simple prototype. High performance and easy to understand.
**Alternatives:** React or Vue (overkill for this simple Q&A bot).

### 3. Modular Processor Interface
**Decision:** Define a `ChatProcessor` class or function in a dedicated module (e.g., `muggle/ai.py`).
**Rationale:** This decouples the Flask route from the AI implementation. The Flask route will call `processor.get_response(text)`, which initially uses a DeepSeek model via LangChain but can be replaced by a LangGraph workflow later.
**Alternatives:** Hardcoding the LLM logic in the Flask route (rejected as it violates the extensibility goal).

### 4. LLM Choice
**Decision:** Use DeepSeek as the primary LLM model.
**Rationale:** DeepSeek is part of the project's established tech stack (as per GEMINI.md) and provides strong performance for Q&A tasks.
**Alternatives:** DashScope (available in stack, but DeepSeek selected for this iteration).

## Risks / Trade-offs

- **[Risk]** In-memory history won't scale. → **Mitigation**: This is an MVP; persistent storage is out of scope.
- **[Risk]** LangGraph integration might require interface changes. → **Mitigation**: Design the `ChatProcessor` to accept a message and return a string (or stream) to stay flexible.
