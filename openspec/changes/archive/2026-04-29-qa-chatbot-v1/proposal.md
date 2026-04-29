# Proposal: Simple Q&A Chatbot (v1)

## Problem Statement
The project currently has a boilerplate structure but no functional AI interaction. We need a basic Q&A chatbot that serves as a foundation for future development, adhering to the project's tech stack (Flask, LangChain/LangGraph) while keeping the initial implementation simple.

## Proposed Changes
We will implement a minimal "Muggle Chat" application consisting of:
- **Frontend:** A single-page application (SPA) using vanilla HTML/CSS/JS for a clean, responsive chat interface.
- **Backend:** A Flask-based API with a single `/chat` endpoint.
- **AI Core:** A modular "Processor" interface. 
    - Initially, this will be a simple LLM wrapper (LangChain).
    - Crucially, it will be architected to allow swapping in a **LangGraph** workflow without modifying the API or UI.

## Goals
- Provide a functional web-based chat interface.
- Establish the communication pattern between Frontend and Backend.
- Create a clear integration point for LangGraph state machines.

## Non-Goals
- Complex multi-agent workflows (deferred to v2).
- User authentication or persistent database storage (beyond simple in-memory session history).
- Advanced styling or UI frameworks.

## Tech Stack
- **Backend:** Python, Flask.
- **AI:** LangChain (LLM abstraction), DeepSeek.
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API).
