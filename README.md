# RMIT Cyber Security Course Advisor — Python (Streamlit)

**Purpose:**
- A Streamlit chatbot that helps RMIT students explore and choose courses in the Bachelor of Cyber Security (BP355 / BP356).
- Uses local structured JSON or uploaded PDFs as the knowledge source and calls AWS Bedrock (Anthropic Claude) via Cognito authentication.

**Repository layout**
- `app.py` — main Streamlit application (login page, chat UI, data loaders, Bedrock integration).
- `requirements.txt` — Python dependencies.
- `courses_data.json` — preloaded structured course data (optional; app will load automatically if present).
- `cyber_security_program_structure.json` — preloaded study-structure (optional).
- `Fw_ BP355 enrolment project/` — optional folder with original PDF documents used for testing unstructured input.

**Key features**
- Login page: enter Cognito USERNAME and PASSWORD (stored in session state) before using the app. Credentials are used to obtain temporary AWS credentials for Bedrock calls.
- Two input modes:
  - Structured JSON (preloaded): app reads `courses_data.json` and program structure file from the project folder automatically.
  - Unstructured PDF: upload one or more PDF documents; the app extracts text and builds a prompt for the model.
- Vertical chat layout: conversation appears in a vertical stream like typical chat UIs. Messages render immediately after sending and after the assistant reply.
- Bedrock / Claude integration: prompts are sent to the configured model (set in `app.py`). Responses appear as assistant messages in the chat.
- Prompt building: when JSON mode is used, the app builds a detailed prompt including course listings and recommended study structure to guide the model.

---

## 🗂️ Preparation

### 📁 Step 0: Download Starter Files

* Download the ZIP package from Canvas: `Assignment3_Chatbot_Python.zip`
* Unzip the folder to a known location (e.g., Desktop)
* The folder structure looks like this:

```
Assignment3_Chatbot_Python/
├── app.py
├── requirements.txt
├── chatbot_logic.py
├── Fw_ BP355 enrolment project/   <- raw PDFs
├── courses_data.json
├── cyber_security_program_structure.json
```

---

## 🧰 Step 1: Check Python Version

### ✅ Requirement: Python 3.11

Open Terminal (macOS) or Command Prompt / PowerShell (Windows), and run:

```bash
python --version
```

If the version is **not 3.11.x**, download and install it from: [https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)

---

## 🐍 Step 2: Set Up Virtual Environment (Recommended)

In your terminal, navigate into the unzipped folder:

```bash
cd path/to/Assignment3_Chatbot_Python
```

Create and activate a virtual environment:

### Windows:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 📦 Step 3: Install Dependencies

Don't forget to paste your username and password inside to the app.py

Signup at here:

https://ap-southeast-2nfozbdvjd.auth.ap-southeast-2.amazoncognito.com/login?client_id=3p3lrenj17et3qfrnvu332dvka&response_type=code&scope=email+openid+phone&redirect_uri=https%3A%2F%2Fd84l1y8p4kdic.cloudfront.net

```
USERNAME = "" # Replace with your username
PASSWORD = ""    # Replace with your password
```

You can choose one of these model as you like:

anthropic.claude-3-haiku-20240307-v1:0
 
anthropic.claude-3-5-sonnet-20241022-v2:0
 

Once your virtual environment is activated, install all dependencies:

```bash
pip install -r requirements.txt
```

If installation is successful, you’ll return to the prompt without errors.

Sometimes, You might see the warning like 'Import "streamlit" could not be resolvedPylancereportMissingImports' in your VS Code editor. Don't worry — this warning is from the VS Code language server (Pylance) and does not affect code execution as long as streamlit is installed correctly.

This usually happens when:

VS Code is not using the correct Python interpreter (e.g. your virtual environment), or

The language server hasn't picked up the environment changes yet.

✅ If you have already installed the requirements and can run the app using:

streamlit run app.py
then everything is working as expected, and you can safely ignore this warning.


---

## 🚀 Step 4: Run the Chatbot

To launch the chatbot UI:

```bash
streamlit run app.py
```

This will open a browser window with your chatbot interface.

### Quick run (Windows PowerShell)

If `streamlit` is installed but the `streamlit` command is not found, run Streamlit with the interpreter on your PATH:

```powershell
python -m streamlit run app.py
```

Streamlit may prompt for an optional email address in the terminal; you can leave it blank and press Enter. To stop the server, press Ctrl+C in the PowerShell window.


---

## 📂 Step 5: Upload Course Data

In the chatbot UI:

1. Choose upload mode: `Structured JSON` or `PDF`
2. Upload the following (if using JSON mode):

   * `courses_data.json`
   * `cyber_security_program_structure.json`


You can also upload the original PDFs from the `data/Fw_ BP355 enrolment project` folder for testing unstructured sources.

---

## 💬 Step 6: Start Chatting

Type a question such as:

* *"What’s the difference between COSC2626 and INTE2402?"*
* *"How do I enrol in COSC1111?"*

The chatbot will respond based on the uploaded data.


---

## ❓ Troubleshooting

| Issue                          | Solution                                                      |
| ------------------------------ | ------------------------------------------------------------- |
| `streamlit: command not found` | Make sure virtual environment is activated                    |
| Cannot install packages        | Ensure you have Python 3.11 and pip is working                |
| No browser opens               | Visit [http://localhost:8501](http://localhost:8501) manually |
| Data not loaded properly       | Check file formats and filenames                              |

---

## ✅ Done!

You now have a fully working Assignment 3 chatbot. You can begin answering assignment questions and improving your knowledge base.

For more advanced tasks (prompt tuning, data cleaning, documentation), please refer to the **Course Enrolment Chatbot Handbook**.

---

© RMIT COSC1111/COSC3113 - Oct 2025
