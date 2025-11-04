# RMIT Cyber Security Course Advisor — Python (Streamlit)

Overview
- Streamlit chatbot to help RMIT students explore and choose courses in the Bachelor of Cyber Security (BP355 / BP356).
- Uses preloaded structured JSON or uploaded PDFs as the knowledge source and calls AWS Bedrock (Anthropic Claude) via Cognito authentication.

Key features
- Login: enter Cognito USERNAME and PASSWORD (stored in session_state) to get temporary Bedrock credentials.
- Two data input modes:
  - Structured JSON (preloaded): reads `courses_data.json` and `cyber_security_program_structure.json` automatically.
  - Unstructured PDFs: upload PDF(s); text is extracted, cleaned and used as context.
- Vertical chat UI: single-column, chronological chat like ChatGPT. Messages render immediately.
- Automatic client-side memory:
  - Short-term context: recent N turns are injected automatically.
  - Long-term memory: model-generated conversation summary is created periodically and injected into prompts.
  - Memory is seamless — no extra user steps required.
- Prompt editing: generated prompts are visible and editable before being sent to the model (auditability & control).
- Real-time responses: model output is streamed incrementally to the UI (when model/endpoint supports chunked responses).
- Model selection: choose between available Bedrock model IDs in the sidebar:
  - anthropic.claude-3-5-sonnet-20241022-v2:0
  - anthropic.claude-3-haiku-20240307-v1:0
- Data cleaning: extracted text is cleaned (headers/footers removed, whitespace normalized, truncation) to reduce noise and token use.
- (Optional) Future: vector indexing / embeddings for large-document retrieval.

Repository layout
- `app.py` — main Streamlit app (login, chat UI, data loaders, Bedrock integration).
- `requirements.txt` — Python dependencies.
- `courses_data.json` — preloaded structured course data (optional).
- `cyber_security_program_structure.json` — preloaded study structure (optional).
- `Fw_ BP355 enrolment project/` — optional PDFs for testing.

How it works (high level)
1. User logs in with Cognito username/password.
2. App exchanges credentials for temporary AWS credentials and uses them to call Bedrock.
3. The app builds a prompt from:
   - preloaded JSON or cleaned PDF text,
   - automatic conversation summary (long-term memory),
   - recent conversation turns (short-term memory),
   - the user's current question.
4. Optionally the user edits the prompt, then sends it to the selected model.
5. The model response is streamed (if available), shown in the chat and appended to conversation history.
6. Periodically the app asks the model to summarize older turns into the long-term conversation summary to keep context compact.

| Function | Description |
|----------|-------------|
| `get_credentials(username, password)` | Exchange Cognito username/password for temporary AWS credentials (Identity Pool) used to call Bedrock. |
| `build_prompt(courses, user_question, structure=None)` | Create a detailed textual prompt from structured JSON course data and optional program structure; appends the user's question. |
| `build_prompt_with_context(base_context, user_question)` | Compose the final prompt by injecting long-term summary + recent turns + base context + current question (used for memory). |
| `extract_text_from_pdfs(pdf_files)` | Read uploaded PDFs page-by-page, extract text, and return a combined cleaned text block for use in prompts. |
| `load_default_jsons()` | Load the two structured JSON files (`courses_data.json`, `cyber_security_program_structure.json`) from the app folder if present. |
| `invoke_bedrock(prompt_text, username, password, max_tokens=..., temperature=..., top_p=...)` | Call AWS Bedrock (Anthropic model) with the built prompt using temp credentials; returns the model response (synchronous). |
| `recent_messages_text(messages, window=CONTEXT_WINDOW)` | Produce a compact text representation of the most recent conversation turns to include in prompts. |
| `summarize_conversation(username, password)` | Ask the model to summarise older conversation turns into a short bullet-list summary stored in session state (long-term memory). |
| `render_messages()` | Render the chat history from session_state into the single-column chat container (keeps UI consistent). |


Quick start (Windows)
1. Open PowerShell and navigate to the project folder:
   cd "c:\path\to\Assignment3_Chatbot_Python"
2. Create and activate venv:
   python -m venv .venv
   .\.venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Run app:
   python -m streamlit run app.py

Configuration notes
- Place `courses_data.json` and `cyber_security_program_structure.json` next to app.py to use Structured JSON mode.
- Cognito / Bedrock settings live at the top of app.py (COGNITO_REGION, MODEL_ID, IDENTITY_POOL_ID, USER_POOL_ID, APP_CLIENT_ID). Do not commit secrets.
- Provide valid Cognito username/password at the login screen (the app exchanges these for temporary AWS credentials at runtime).
- Model selection is available in the sidebar.

Security & privacy
- Do NOT hardcode or commit secrets (AWS keys, passwords). This app stores login in session_state only while the session runs.
- Uploaded PDFs and conversation data are processed in memory. If you enable persistence, encrypt or restrict access and add a privacy notice.

Troubleshooting
- streamlit command not found: ensure venv is active or run python -m streamlit run app.py
- Missing JSON files: place required files next to app.py or use PDF mode
- Authentication errors: check username/password and Cognito configuration; network access is required.

Development notes
- Important functions to inspect: prompt builder (build_prompt / build_prompt_with_context), PDF extractor & cleaner, invoke_bedrock (sync and streaming), summarize_conversation.
- Suggested improvements: background summarization, persistent memory store, embeddings + FAISS for retrieval, unit tests for cleaning & prompt builder.

License / attribution
- Course material and code adapted for RMIT COSC1111 / Assignment 3 (Oct 2025). Use for learning and assignment purposes only.
```// filepath: c:\Users\ryanj\OneDrive\Documents\__2 Uni Files\RMIT\COSC1111\Assignment3_Chatbot_Python\README.md
# RMIT Cyber Security Course Advisor — Python (Streamlit)