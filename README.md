# CRM Follow-Up Agent

A demonstration CRM agent built with:

- LangGraph for agent workflow/orchestration
- MCP for standardized CRM tools
- SQLite for mock CRM data
- Streamlit for the chat UI
- OpenAI Chat Model for reasoning

## Architecture

```text
User
  |
  v
Streamlit
  |
  v
LangGraph
  |
  v
LangChain tools
  |
  v
MCP Client
  |
  | MCP / Streamable HTTP
  v
MCP Server
  |
  +--> Customer tools
  +--> Invoice tools
  +--> Follow-up tools
  +--> Reminder/update tools
  |
  v
SQLite
```

## Project files

```text
crm_followup_agent/
├── app.py
├── agent.py
├── mcp_server.py
├── mcp_client.py
├── db.py
├── seed_db.py
├── requirements.txt
├── .env.example
├── README.md
└── data/
    └── crm.db       # created automatically
```

## Setup on Windows / VS Code

Open the project folder in VS Code.

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create `.env`

Copy `.env.example` to `.env` and put your OpenAI API key inside:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
MCP_SERVER_URL=http://127.0.0.1:8000/mcp
```

### 4. Create/reset the demo database

```powershell
python db.py
```

This creates fictional customers, invoices and follow-ups.

### 5. Run the application

```powershell
streamlit run app.py
```

The Streamlit app automatically starts `mcp_server.py`.

## Optional: run the MCP server separately

For learning/debugging, you can also use two terminals.

Terminal 1:

```powershell
python mcp_server.py
```

Terminal 2:

```powershell
streamlit run app.py
```

## Useful demo questions

```text
Show me all overdue invoices.

Who owes us the most money?

What does ABC Technologies owe us?

Show me the follow-up history for ABC Technologies.

What follow-ups are coming up?

Which customers have not responded?

Prepare a payment reminder for ABC Technologies.

Send the payment reminder for ABC Technologies for INV001.
```

## Important demo behavior

The `send_payment_reminder` MCP tool is intentionally a mock action.

It records the reminder in SQLite but DOES NOT send a real email.

This makes the project safe to demonstrate while still showing an MCP
state-changing tool.

## What to learn after it runs

1. `mcp_server.py` — how MCP tools are exposed
2. `mcp_client.py` — how an MCP client calls those tools
3. `agent.py` — how LangGraph controls the agent/tool loop
4. `db.py` — where the CRM information actually lives
5. `app.py` — how the Streamlit UI connects everything