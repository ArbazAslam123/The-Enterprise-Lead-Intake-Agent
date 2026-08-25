# ⚡ Enterprise AI Lead Intake & CRM Triage Agent

An autonomous, multi-tool agentic intake system built with **LangGraph**, **Groq (`openai/gpt-oss-120b`)**, and **Streamlit**.

The system engages prospective enterprise clients in natural conversation, qualifies inbound leads, extracts structured parameters — **Client Name, Company, Project Scope, and Budget** — and automatically dispatches live API actions to **Google Sheets** as an analytics database and **ClickUp** as the sales CRM.

---

## 🏗️ Architecture & Execution Flow

```text
              +-------------------------+
              |       User Prompt       |
              +------------+------------+
                           |
                           v
              +-------------------------+
              |  Assistant (LangGraph) |
              +------------+------------+
                           |
                  [ Tools Condition ]
                           |
           +---------------+---------------+
           |                               |
     (Missing Info)                 (All 4 Entities)
           |                               |
           v                               v
   +---------------+              +-----------------+
   | Converse / Ask|              |    ToolNode     |
   +-------+-------+              +--------+--------+
           |                               |
           v                    +----------+----------+
         [ END ]                 |                     |
                                 v                     v
                       +-------------------+   +----------------------+
                       | log_lead_to_      |   | create_clickup_task  |
                       | sheets            |   |                      |
                       | Google Sheets API |   | ClickUp REST API     |
                       +---------+---------+   +----------+-----------+
                                 |                        |
                                 +-----------+------------+
                                             |
                                             v
                                  +----------------------+
                                  |  Execution Results   |
                                  +----------+-----------+
                                             |
                                             v
                                  +----------------------+
                                  | Assistant Re-invoked |
                                  | Verification & Reply  |
                                  +----------------------+
```

---

## 🔄 How It Works

### 1. Conversational Intake & Entity Extraction

The system uses LangGraph to maintain the conversation state and collect the information required to qualify a lead.

* The graph maintains state using LangGraph's `add_messages` reducer to preserve conversational history without overwriting context.
* A structured system prompt guides the LLM to collect four specific data points:

  * **Full Name**
  * **Company Name**
  * **Project Scope**
  * **Estimated Budget**
* If information is missing, the agent continues the conversation naturally and asks only for the required details.
* Backend integrations are not triggered until all required parameters have been collected.

### 2. Multi-Tool Function Calling

Once all four required data points are available, the model generates structured tool calls.

#### 📊 `log_lead_to_sheets`

Connects to Google Sheets using a **Google Cloud Service Account** through `gspread`.

The tool:

* Opens the `AI_Lead_Intake_DB` spreadsheet.
* Appends a timestamped lead record.
* Stores the client's name, company, budget, project request, and status.
* Creates an immutable record for analytics and lead tracking.

#### 📋 `create_clickup_task`

Creates a sales task using the **ClickUp REST API v2**.

The tool:

* Sends an authenticated `POST` request to ClickUp.
* Creates a task inside the configured ClickUp List.
* Generates a Markdown-formatted lead triage briefing.
* Dynamically determines task priority based on the estimated budget.
* Applies relevant metadata and tags.

### 3. Loop Closure & Verification

After the tools execute:

1. `ToolNode` executes the requested integrations.
2. Each integration returns a `ToolMessage` containing its execution result.
3. The results are added back into the LangGraph state.
4. The assistant node is invoked again.
5. The orchestrator verifies the execution results.
6. A finalized confirmation is presented to the user.

This creates a complete workflow:

```text
User
  ↓
Conversational Intake
  ↓
Entity Extraction
  ↓
Validation
  ↓
Conditional Routing
  ↓
Google Sheets + ClickUp
  ↓
Execution Verification
  ↓
Final Confirmation
```

---

## 🛠️ Tech Stack

| Category                     | Technology                             |
| ---------------------------- | -------------------------------------- |
| **Orchestration & Workflow** | LangGraph, LangChain Core              |
| **LLM Engine**               | Groq API (`openai/gpt-oss-120b`)       |
| **Google Integration**       | Google Sheets API, Google Drive API    |
| **Google Client Libraries**  | `gspread`, `google-auth`               |
| **CRM Integration**          | ClickUp REST API v2                    |
| **HTTP Client**              | `requests`                             |
| **Frontend**                 | Streamlit                              |
| **Environment Management**   | `python-dotenv`                        |
| **Authentication**           | Google Cloud Service Account OAuth 2.0 |

---

## 📁 Repository Structure

```text
ai-lead-intake-agent/
│
├── app.py
│   └── Streamlit reactive UI with state tracking and execution status
│
├── lead_intake_agent.py
│   └── LangGraph workflow, state schemas, routing, and system prompt
│
├── google_sheets_tool.py
│   └── Google Cloud Service Account integration and sheet appender
│
├── clickup_tool.py
│   └── ClickUp REST API client and task generator
│
├── requirements.txt
│   └── Project dependencies
│
├── .env.example
│   └── Template for required environment variables
│
├── .gitignore
│   └── Credential and cache protection rules
│
└── README.md
    └── Project documentation
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/ai-lead-intake-agent.git
cd ai-lead-intake-agent
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Configure Google Cloud Service Account

The Google Sheets integration uses a Google Cloud Service Account.

### Step 1 — Create a Google Cloud Project

Go to the **Google Cloud Console** and create a new project.

### Step 2 — Enable Required APIs

Enable:

* **Google Sheets API**
* **Google Drive API**

### Step 3 — Create a Service Account

Create a **Service Account**, generate a **JSON key**, and download the credentials.

Rename the downloaded file to:

```text
google_credentials.json
```

Place it in the project root:

```text
ai-lead-intake-agent/
├── google_credentials.json
├── app.py
├── lead_intake_agent.py
└── ...
```

> ⚠️ **Never commit `google_credentials.json` to GitHub.**

### Step 4 — Create the Google Sheet

Create a Google Sheet named:

```text
AI_Lead_Intake_DB
```

Add the following headers in Row 1:

```text
Date | Name | Company | Budget | Project Request | Status
```

### Step 5 — Share the Spreadsheet

Open `google_credentials.json` and find the:

```text
client_email
```

Share the Google Sheet with this email address and give it **Editor** permissions.

---

# 📋 Configure ClickUp

The agent uses the ClickUp REST API to create CRM tasks automatically.

### Step 1 — Generate an API Token

Log in to ClickUp and navigate to:

```text
Settings → Apps → API Token
```

Generate a **Personal API Token**.

Your token will look similar to:

```text
pk_...
```

### Step 2 — Find Your List ID

Open the ClickUp List where you want qualified leads to be created.

The List ID can be found in the ClickUp URL:

```text
https://app.clickup.com/{team_id}/v/li/{list_id}
```

Copy the numeric `list_id`.

---

# 🔑 Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_groq_api_key
CLICKUP_API_KEY=pk_your_clickup_personal_token
CLICKUP_LIST_ID=your_numeric_list_id
```

Your project should now contain:

```text
ai-lead-intake-agent/
├── .env
├── google_credentials.json
├── app.py
├── lead_intake_agent.py
├── google_sheets_tool.py
├── clickup_tool.py
└── ...
```

> ⚠️ Add both `.env` and `google_credentials.json` to `.gitignore`.

---

# 🖥️ Running the Application

## Local CLI Test

To test the LangGraph workflow directly:

```bash
python lead_intake_agent.py
```

## Launch the Streamlit Interface

Run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL where you can interact with the lead intake agent.

---

# ☁️ Deploying to Streamlit Community Cloud

Before deployment, make sure that:

* `.env` is **not committed**
* `google_credentials.json` is **not committed**
* API keys are stored securely in Streamlit Secrets

### 1. Push the Repository to GitHub

Push your project to GitHub without exposing any credentials.

### 2. Connect the Repository

Open Streamlit Community Cloud and connect your GitHub repository.

Select:

```text
app.py
```

as the application entry point.

### 3. Configure Streamlit Secrets

In:

```text
Advanced Settings → Secrets
```

add your environment variables:

```toml
GROQ_API_KEY = "gsk_your_groq_api_key"
CLICKUP_API_KEY = "pk_your_clickup_personal_token"
CLICKUP_LIST_ID = "your_clickup_list_id"
```

### 4. Add Google Cloud Credentials

You can also store the Google Service Account credentials directly in Streamlit Secrets:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
```

> **Security Note:** Never publish your API keys, private keys, service account JSON, or `.env` file in your GitHub repository.

---

# 🔄 End-to-End Workflow

The complete agentic workflow can be summarized as:

```text
                ┌──────────────────┐
                │   Potential Lead │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Conversational   │
                │ Intake Agent     │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Extract Lead     │
                │ Entities         │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ All Required     │
                │ Data Available?  │
                └───────┬──────────┘
                    No   │   Yes
                    ↓    │    ↓
              ┌────────┐ │ ┌──────────────────┐
              │  Ask   │ │ │   ToolNode       │
              │ Again  │ │ └────────┬─────────┘
              └────────┘ │          ↓
                         │    ┌─────┴─────┐
                         │    ↓           ↓
                         │ Google      ClickUp
                         │ Sheets       CRM
                         │    ↓           ↓
                         └────┬───────────┘
                              ↓
                    ┌──────────────────┐
                    │ Verify Execution │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Final Response   │
                    └──────────────────┘
```

---

# 🎯 Project Goal

The goal of this project is to demonstrate a practical **agentic AI lead qualification and CRM automation architecture**.

Instead of simply generating text, the system can:

* 💬 Communicate naturally with prospective clients
* 🧠 Extract structured lead information
* 🔎 Determine when sufficient information has been collected
* 🔀 Route execution using LangGraph
* 📊 Store qualified leads in Google Sheets
* 📋 Create actionable CRM tasks in ClickUp
* ⚡ Execute multiple backend integrations automatically
* ✅ Verify tool execution before providing the final response

### Core Architecture

```text
User Query
    ↓
AI Lead Intake
    ↓
Entity Extraction
    ↓
Validation
    ↓
LangGraph Conditional Routing
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
Google Sheets     ClickUp CRM
│                 │
└─────────────────┴─────────────────┘
              ↓
      Execution Verification
              ↓
       Final Confirmation
```

---

## 🔒 Security Checklist

Before pushing the project to GitHub, verify that the following files are excluded:

```gitignore
.env
google_credentials.json
__pycache__/
*.pyc
venv/
.venv/
.streamlit/secrets.toml
```

**Never expose:**

* Groq API keys
* ClickUp API tokens
* Google Service Account private keys
* `.env` files
* Streamlit secrets
* Google credential JSON files
