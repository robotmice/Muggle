## 1. Backend Setup

- [x] 1.1 Create `muggle/app.py` with basic Flask configuration
- [x] 1.2 Implement `POST /chat` endpoint in `app.py`
- [x] 1.3 Add basic error handling for missing payload fields

## 2. AI Processor Interface

- [x] 2.1 Create `muggle/ai.py` to house the AI logic
- [x] 2.2 Implement `ChatProcessor` class with a `get_response(message)` method
- [x] 2.3 Integrate DeepSeek LLM via LangChain

## 3. Frontend Implementation

- [x] 3.1 Create `muggle/static/index.html` with a basic chat layout
- [x] 3.2 Implement JavaScript `sendMessage` function to fetch from `/chat`
- [x] 3.3 Add minimal CSS for chat bubble styling and responsive layout

## 4. Integration & Verification

- [x] 4.1 Connect the Flask route to the `ChatProcessor`
- [x] 4.2 Verify the end-to-end flow: User input -> Flask -> AI -> Response display
- [x] 4.3 Add a basic unit test for the `ChatProcessor` interface
