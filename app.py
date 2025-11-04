# Cyber Security Course Advisor via AWS Bedrock
# Author: Cyrus Gao, extended by Xiang Li
# Updated: May 2025

import streamlit as st
import json
import boto3
from PyPDF2 import PdfReader
from pathlib import Path

# === AWS Configuration === #
COGNITO_REGION = "ap-southeast-2"
BEDROCK_REGION = "ap-southeast-2"
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
IDENTITY_POOL_ID = "ap-southeast-2:eaa059af-fd47-4692-941d-e314f2bd5a0e"
USER_POOL_ID = "ap-southeast-2_NfoZbDvjD"
APP_CLIENT_ID = "3p3lrenj17et3qfrnvu332dvka"

# Default placeholders (will be overridden by login)
USERNAME = ""
PASSWORD = ""

# === Helper: Get AWS Credentials === #
def get_credentials(username, password):
    idp_client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
    response = idp_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=APP_CLIENT_ID,
    )
    id_token = response["AuthenticationResult"]["IdToken"]

    identity_client = boto3.client("cognito-identity", region_name=COGNITO_REGION)
    identity_response = identity_client.get_id(
        IdentityPoolId=IDENTITY_POOL_ID,
        Logins={f"cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    creds_response = identity_client.get_credentials_for_identity(
        IdentityId=identity_response["IdentityId"],
        Logins={f"cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    return creds_response["Credentials"]


# === Helper: Build Prompt from JSON + Structure === #
def build_prompt(courses, user_question, structure=None):
    course_dict = {c["title"]: c for c in courses}

    structure_text = ""
    if structure and "recommended_courses" in structure:
        structure_text += "### Recommended Study Plan by Year:\n"
        for year, course_titles in structure["recommended_courses"].items():
            structure_text += f"**{year.replace('_', ' ').title()}**:\n"
            for title in course_titles:
                course = course_dict.get(title)
                if course:
                    structure_text += f"- {title} ({course['course_code']})\n"
                else:
                    structure_text += f"- {title} (not found in course list)\n"
            structure_text += "\n"

    course_list = []
    for course in courses:
        title = course.get("title", "Untitled")
        code = course.get("course_code", "N/A")
        desc = course.get("description", "No description available.")
        course_type = course.get("course_type", "N/A")
        minor = course.get("minor_track", [])
        minor_info = f", Minor: {minor[0]}" if minor else ""
        course_text = f"- {title} ({code}): {desc}\n  Type: {course_type}{minor_info}"
        course_list.append(course_text)
    full_course_context = "\n".join(course_list)

    prompt = (
        "You are a helpful assistant that supports students in selecting courses from the "
        "Bachelor of Cyber Security program at RMIT (codes BP355/BP356). "
        "Recommend only from the official course list. Each course is categorized as core, capstone, minor, or elective. "
        "Use the recommended structure to suggest suitable courses based on study year and interest.\n\n"
        + structure_text
        + "\n### All Available Courses:\n"
        + full_course_context
        + "\n\nUser:\n" + user_question
    )
    return prompt


# === Helper: Extract text from multiple PDFs === #
def extract_text_from_pdfs(pdf_files):
    all_text = []
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text.strip())
        except Exception as e:
            all_text.append(f"[Error reading file {getattr(pdf_file, 'name', 'uploaded')}: {str(e)}]")
    return "\n\n".join(all_text)


# === Helper: Invoke Claude via Bedrock === #
def invoke_bedrock(prompt_text, username, password, max_tokens=640, temperature=0.3, top_p=0.9):
    # Acquire temporary credentials using the provided login (from the login page)
    credentials = get_credentials(username, password)

    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=BEDROCK_REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"],
    )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": [{"role": "user", "content": prompt_text}]
    }

    response = bedrock_runtime.invoke_model(
        body=json.dumps(payload),
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# === Load default structured JSON files from project folder === #
def load_default_jsons():
    base = Path(__file__).parent
    courses_path = base / "courses_data.json"
    structure_path = base / "cyber_security_program_structure.json"
    courses = None
    structure = None
    try:
        if courses_path.exists():
            with open(courses_path, "r", encoding="utf-8") as f:
                courses = json.load(f)
    except Exception:
        courses = None
    try:
        if structure_path.exists():
            with open(structure_path, "r", encoding="utf-8") as f:
                structure = json.load(f)
    except Exception:
        structure = None
    return courses, structure


# --- Simple client-side memory / context tracking configuration ---
CONTEXT_WINDOW = 6            # number of recent turns to include
SUMMARY_INTERVAL = 8          # summarise after this many total messages
SUMMARY_MAX_TOKENS = 256

if "conversation_summary" not in st.session_state:
    st.session_state["conversation_summary"] = ""  # condensed long-term memory

def recent_messages_text(messages, window=CONTEXT_WINDOW):
    if not messages:
        return ""
    recent = messages[-window:]
    parts = []
    for m in recent:
        role = "User" if m["role"] == "user" else "Assistant"
        parts.append(f"{role}: {m['content']}")
    return "\n".join(parts)

def summarize_conversation(username, password):
    """Ask the model to produce a short summary of the conversation so far and store it."""
    messages = st.session_state.get("messages", [])
    if not messages:
        return ""
    convo_text = "\n".join([f"{('User' if m['role']=='user' else 'Assistant')}: {m['content']}" for m in messages])
    prompt = (
        "You are a system that produces a concise summary of a conversation between a user and an assistant.\n\n"
        "Conversation:\n"
        + convo_text
        + "\n\nProvide a short bullet-list summary (3-6 bullets) capturing the user's goals, preferences, constraints and any decisions."
    )
    try:
        summary = invoke_bedrock(prompt, username, password, max_tokens=SUMMARY_MAX_TOKENS, temperature=0.0)
        st.session_state["conversation_summary"] = summary.strip()
        return st.session_state["conversation_summary"]
    except Exception:
        # keep existing summary if summarization fails
        return st.session_state.get("conversation_summary", "")

def build_prompt_with_context(base_prompt, user_question):
    """Combine long-term summary + recent turns + base prompt (courses/pdf) + new question."""
    summary = st.session_state.get("conversation_summary", "")
    recent = recent_messages_text(st.session_state.get("messages", []), window=CONTEXT_WINDOW)
    sections = []
    if summary:
        sections.append("Conversation summary (long-term memory):\n" + summary + "\n")
    if recent:
        sections.append("Recent conversation (most recent first):\n" + recent + "\n")
    sections.append("Context data:\n" + base_prompt + "\n")
    sections.append("User's new question:\n" + user_question + "\n")
    return "\n\n".join(sections)

# === Streamlit UI: Setup and Session State === #
st.set_page_config(page_title="RMIT Cyber Security Course Advisor", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "password" not in st.session_state:
    st.session_state["password"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # list of {"role": "user"/"assistant", "content": "..."}
if "courses" not in st.session_state:
    st.session_state["courses"], st.session_state["structure"] = load_default_jsons()

# === StreamLit starts making the page === #
st.sidebar.title("\U0001F393 Cyber Security Course Advisor")
st.sidebar.markdown("This assistant helps students in RMIT's Bachelor of Cyber Security (BP355/BP356) choose courses.")

# --- Login Page ---
if not st.session_state["authenticated"]:
    st.subheader("Login")
    with st.form("login_form"):
        input_user = st.text_input("Username (email)", value=st.session_state["username"])
        input_pass = st.text_input("Password", value=st.session_state["password"], type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        # store credentials in session (they will be used for Bedrock calls)
        st.session_state["username"] = input_user.strip()
        st.session_state["password"] = input_pass
        if not st.session_state["username"] or not st.session_state["password"]:
            st.warning("Enter both username and password.")
        else:
            # Do not attempt to validate here to avoid unnecessary AWS calls on login.
            st.session_state["authenticated"] = True
            st.rerun()

    st.info("Enter your Cognito username/password to proceed. The structured JSON files are loaded from the project folder automatically.")
    # Show whether default JSONs found
    if st.session_state["courses"] is None or st.session_state["structure"] is None:
        st.warning("Default JSON files not found in project folder. Place 'courses_data.json' and 'cyber_security_program_structure.json' next to app.py or use PDF mode after login.")
    st.stop()

# --- Main App (after login) ---
st.sidebar.markdown("---")

st.sidebar.subheader("Choose your data input format")
upload_mode = st.sidebar.radio("Select format:", ["Structured JSON files (preloaded)", "Unstructured PDF files"])

# For structured mode, the two JSON files are already loaded from disk.
if upload_mode == "Structured JSON files (preloaded)":
    if st.session_state.get("courses") is None or st.session_state.get("structure") is None:
        st.sidebar.error("Structured JSON files not found. Place 'courses_data.json' and 'cyber_security_program_structure.json' next to app.py.")
    else:
        st.sidebar.success("Structured course data loaded from project folder.")
    uploaded_pdfs = None
else:
    uploaded_pdfs = st.sidebar.file_uploader("\U0001F4C4 Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)
    # Clear structured preloaded message if exists
    # uploaded_* JSON uploaders removed per request (files are preloaded)

# --- Model selection (sidebar) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Model selection")
model_choice = st.sidebar.radio(
    "Select Bedrock model:",
    [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
    ],
    index=0 if MODEL_ID == "anthropic.claude-3-5-sonnet-20241022-v2:0" else 1,
)
# update MODEL_ID so invoke_bedrock uses the selected model
MODEL_ID = model_choice

st.sidebar.markdown("---")
st.sidebar.markdown(f"Logged in as: `{st.session_state['username']}`")

# --- Chat / Conversation UI (vertical layout) ---
# persistent placeholder so we can clear-and-redraw cleanly
chat_placeholder = st.empty()

def render_messages():
    # clear previous render and redraw once (avoids duplicate outputs across reruns)
    chat_placeholder.empty()
    with chat_placeholder.container():
        for msg in st.session_state["messages"]:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")
                st.markdown("---")

# initial render (top-level)
render_messages()

st.markdown("----")
with st.form("ask_form", clear_on_submit=True):
    user_input = st.text_input("Ask a question about courses:", key="user_input")
    ask = st.form_submit_button("Send")
    if ask:
        if not user_input:
            st.warning("Please enter a question.")
        else:
            # Append user message and immediately render so it appears right away
            st.session_state["messages"].append({"role": "user", "content": user_input})
            render_messages()

            # Build prompt based on mode
            try:
                if upload_mode == "Structured JSON files (preloaded)":
                    courses = st.session_state.get("courses")
                    structure = st.session_state.get("structure")
                    if not courses or not structure:
                        st.error("Structured data missing. Cannot answer.")
                        st.stop()
                    base_prompt = build_prompt(courses, "", structure)   # base context only
                else:
                    if not uploaded_pdfs:
                        st.error("Please upload at least one PDF file for unstructured mode.")
                        st.stop()
                    extracted_text = extract_text_from_pdfs(uploaded_pdfs)
                    base_prompt = "You are a course advisor. The following is extracted from official course documents:\n\n" + extracted_text

                # build final prompt including memory + recent turns
                prompt = build_prompt_with_context(base_prompt, user_input)

                with st.spinner("\U0001F50D Generating advice..."):
                    answer = invoke_bedrock(prompt, st.session_state["username"], st.session_state["password"])
                # Append assistant reply
                st.session_state["messages"].append({"role": "assistant", "content": answer})
                render_messages()

                # Periodic summarization to compress long-term memory
                total_msgs = len(st.session_state.get("messages", []))
                if total_msgs >= SUMMARY_INTERVAL and total_msgs % SUMMARY_INTERVAL == 0:
                    # summarization will update st.session_state["conversation_summary"]
                    summarize_conversation(st.session_state["username"], st.session_state["password"])
            except Exception as e:
                st.session_state["messages"].append({"role": "assistant", "content": f"[Error]: {str(e)}"})
                render_messages()
    