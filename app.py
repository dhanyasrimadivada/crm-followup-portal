import os
import socket
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agent import build_graph, ask_agent
from db import init_db, seed_db
from mcp_client import list_mcp_tools


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).parent

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://127.0.0.1:8000/mcp",
)


# ---------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CRM Follow-Up Agent",
    page_icon="🤖",
    layout="wide",
)


# ---------------------------------------------------------
# Check MCP server
# ---------------------------------------------------------

def start_mcp_server():
    """
    Check whether the MCP server is running.

    We do not send a normal GET request to /mcp because
    Streamable HTTP MCP expects MCP-specific requests.
    Instead, we simply check whether port 8000 is open.
    """

    try:
        with socket.create_connection(
            ("127.0.0.1", 8000),
            timeout=1
        ):
            return

    except OSError:
        raise RuntimeError(
            "MCP server is not running. "
            "Please run `python mcp_server.py` in another terminal."
        )


# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

init_db()
seed_db()


# ---------------------------------------------------------
# Page title
# ---------------------------------------------------------

st.title("🤖 CRM Follow-Up Agent")

st.caption(
    "LangGraph + MCP + SQLite — demonstration CRM"
)


# ---------------------------------------------------------
# Check Groq API key
# ---------------------------------------------------------

if not os.getenv("GROQ_API_KEY"):

    st.error(
        "GROQ_API_KEY is not configured. "
        "Add it to your .env file."
    )

    st.stop()


# ---------------------------------------------------------
# Check MCP server
# ---------------------------------------------------------

try:

    start_mcp_server()

except Exception as exc:

    st.error(
        f"MCP server startup failed: {exc}"
    )

    st.stop()


# ---------------------------------------------------------
# Build LangGraph agent
# ---------------------------------------------------------

try:

    if "graph" not in st.session_state:

        st.session_state.graph = build_graph()

except Exception as exc:

    st.error(
        f"Agent initialization failed: {exc}"
    )

    st.stop()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("CRM Demo")

    st.write(
        "Ask the agent about customers, "
        "invoices and follow-ups."
    )

    st.markdown("### Try these")

    examples = [

        "Show me all overdue invoices.",

        "Who owes us the most money?",

        "What does ABC Technologies owe us?",

        "Show me the follow-up history for ABC Technologies.",

        "What follow-ups are coming up?",

        "Which customers have not responded to a reminder?",

        "Prepare a payment reminder for ABC Technologies.",

        "Send the reminder to ABC Technologies for INV001.",

    ]

    for example in examples:

        st.markdown(f"- {example}")

    st.divider()


    # -----------------------------------------------------
    # Reset conversation
    # -----------------------------------------------------

    if st.button("🔄 Reset conversation"):

        st.session_state.messages = []

        st.rerun()


    # -----------------------------------------------------
    # Show MCP tools
    # -----------------------------------------------------

    if st.button("🛠️ Show MCP tools"):

        try:

            import asyncio

            tools = asyncio.run(
                list_mcp_tools()
            )

            st.write(tools)

        except Exception as exc:

            st.error(str(exc))


    st.divider()


    st.info(
        "Demo mode: payment reminders update the "
        "local CRM database but do not send real emails."
    )


# ---------------------------------------------------------
# Initialize chat history
# ---------------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# ---------------------------------------------------------
# Display previous messages
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

user_input = st.chat_input(
    "Ask your CRM agent something..."
)


# ---------------------------------------------------------
# Process user question
# ---------------------------------------------------------

if user_input:

    # Add user message to history

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # Display user message

    with st.chat_message("user"):

        st.markdown(user_input)


    # Generate agent response

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking and using CRM tools..."
        ):

            try:

                # Exclude the current message from history
                # because ask_agent() receives it separately.

                history = (
                    st.session_state.messages[:-1]
                )


                response = ask_agent(

                    st.session_state.graph,

                    user_input,

                    history=history,

                )


            except Exception as exc:

                response = (
                    "I hit an error while running "
                    "the CRM agent.\n\n"
                    f"`{exc}`"
                )


        # Display response

        st.markdown(response)


    # Save assistant response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )