# RMIT Cyber Security Course Advisor — Python (Streamlit)

Overview
- A Streamlit chatbot to help RMIT students explore and choose courses in the Bachelor of Cyber Security (BP355 / BP356).
- The app uses either preloaded structured JSON files or uploaded PDF documents as the knowledge source and calls AWS Bedrock (Anthropic Claude models) using Cognito authentication to obtain temporary credentials.

Repository contents
- `app.py` — main Streamlit application (login, chat UI, data loaders, Bedrock integration).
- `requirements.txt` — Python dependencies.
- `courses_data.json` — optional structured course data (used in Structured JSON mode if present).
- `cyber_security_program_structure.json` — optional program-structure data (used in Structured JSON mode if present).
- `Fw_ BP355 enrolment project/` — optional folder for test PDFs.

Key behaviours (current implementation)
- Login: users enter a Cognito username and password on the login page. These are stored in `st.session_state` for the session and are used to exchange for temporary AWS credentials when calling Bedrock.
- Input modes:
  - Structured JSON (preloaded): the app attempts to load `courses_data.json` and `cyber_security_program_structure.json` from the same folder as `app.py` and uses them as the knowledge base.
  - Unstructured PDFs: after login the user can upload one or more PDFs; the app extracts page text and uses that extracted text as prompt context.
- Chat UI: a vertical, single-column chat view where user questions and assistant replies are appended to `st.session_state['messages']` and re-rendered on each interaction.
- Memory and context:
  - Short-term context: the most recent N turns (controlled by `CONTEXT_WINDOW`) are included in prompts.
  - Long-term memory: the app periodically asks the model to summarise older conversation turns into a concise bullet-list summary (`SUMMARY_INTERVAL`, `SUMMARY_MAX_TOKENS`) that is stored in `st.session_state['conversation_summary']` and injected into future prompts.
- Model selection: the sidebar allows selecting the Bedrock model ID; the chosen model is saved into `st.session_state['model_id']` for use when invoking Bedrock.

Important implementation notes (accurate to `app.py`)
- The app programmatically builds prompts from structured JSON or extracted PDF text plus recent conversation and any stored summary, then sends the prompt to Bedrock. There is not a prompt-edit UI for manual editing.
- The `invoke_bedrock` function performs synchronous model invocations (it builds a JSON payload and calls Bedrock via the `bedrock-runtime` client). The app does not currently show chunked/streamed output in the UI.
- `extract_text_from_pdfs` uses PyPDF2's `PdfReader` to extract page text. It does not currently perform advanced header/footer removal or token-aware truncation.

Key configuration values (top of `app.py`)
- COGNITO_REGION, BEDROCK_REGION — AWS regions used for Cognito and Bedrock calls.
- IDENTITY_POOL_ID, USER_POOL_ID, APP_CLIENT_ID — Cognito identifiers used for token exchange and identity.
- MODEL_ID — default Bedrock model id (can be changed in the sidebar at runtime).
- CONTEXT_WINDOW, SUMMARY_INTERVAL, SUMMARY_MAX_TOKENS — control short- and long-term memory behaviour.

Important functions (high level)
- `get_credentials(username, password)` — exchanges the provided Cognito username/password for an IdToken and then obtains temporary AWS credentials via an Identity Pool.
- `build_prompt(courses, user_question, structure=None)` — creates a textual prompt from structured course JSON and optional program structure.
- `build_prompt_with_context(base_prompt, user_question)` — composes the final prompt by injecting the long-term summary and recent messages before the user's new question.
- `extract_text_from_pdfs(pdf_files)` — extracts text from uploaded PDFs and combines page text into a single block.
- `load_default_jsons()` — loads `courses_data.json` and `cyber_security_program_structure.json` if they exist next to `app.py`.
- `invoke_bedrock(prompt_text, username, password, ...)` — exchanges credentials and calls Bedrock synchronously, returning the model text response.

Quick start (Windows PowerShell)
1. Open PowerShell and navigate to the project folder:
   cd "c:\Users\ryanj\OneDrive\Documents\__2 Uni Files\RMIT\COSC1111\Assignment3_Chatbot_Python"
2. Create and activate a virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   python -m streamlit run app.py

Configuration & usage
- For Structured JSON mode, place `courses_data.json` and `cyber_security_program_structure.json` next to `app.py`.
- At login, provide a valid Cognito username/password. The app exchanges these for temporary AWS credentials and uses them only during the session to call Bedrock.
- Review the identifiers at the top of `app.py` and avoid committing secrets or private keys.

Security & privacy
- Do NOT commit AWS secrets or persistent credentials to this repository.
- Uploaded PDFs and conversation contents are processed in memory; if you add persistence, adopt encryption and access controls.

Troubleshooting
- `streamlit` command not found: activate your virtualenv or run `python -m streamlit run app.py`.
- Missing JSON files: place the required JSON files next to `app.py` or use PDF upload mode after login.
- Authentication errors: verify username/password and the Cognito/Identity Pool configuration. Networking to AWS endpoints is required.

Development notes & suggested enhancements
- Add a prompt-preview/edit UI for transparency and auditing.
- Implement streaming/chunked responses if the bedrock runtime supports it and adapt the UI accordingly.
- Improve PDF cleaning (strip headers/footers, page filtering) and add token-aware truncation to avoid oversized prompts.
- Add embeddings + a vector store (FAISS, Milvus) for retrieval on large document sets.
- Add basic unit tests for the prompt builder and PDF extraction.

License / attribution
- Course material and code adapted for RMIT COSC1111 / Assignment 3 (2025). Use for learning and assignment purposes only.