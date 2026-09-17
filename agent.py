import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from mcp_client import call_mcp_tool

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")


def run_mcp(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Bridge synchronous LangGraph tool execution to the async MCP client."""
    try:
        return asyncio.run(call_mcp_tool(tool_name, arguments))
    except RuntimeError as exc:
        # Streamlit normally has no running event loop here.
        # This fallback is useful in environments that do.
        if "asyncio.run()" not in str(exc):
            raise
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(call_mcp_tool(tool_name, arguments))
        finally:
            loop.close()


@tool
def get_customers(search: str = "") -> str:
    """Find CRM customers by company name, contact name, or email."""
    return str(run_mcp("get_customers", {"search": search}))


@tool
def get_customer(customer_id: str) -> str:
    """Get a customer's full CRM profile by customer ID."""
    return str(run_mcp("get_customer", {"customer_id": customer_id}))


@tool
def get_pending_invoices() -> str:
    """Get all unpaid invoices, including pending and overdue invoices."""
    return str(run_mcp("get_pending_invoices", {}))


@tool
def get_overdue_invoices() -> str:
    """Get all overdue invoices and the number of days they are overdue."""
    return str(run_mcp("get_overdue_invoices", {}))


@tool
def get_customer_invoices(customer_id: str) -> str:
    """Get all invoices for one customer."""
    return str(run_mcp("get_customer_invoices", {"customer_id": customer_id}))


@tool
def get_followup_history(customer_id: str) -> str:
    """Get the customer's CRM follow-up and contact history."""
    return str(run_mcp("get_followup_history", {"customer_id": customer_id}))


@tool
def get_upcoming_followups() -> str:
    """Get follow-ups scheduled for today or a future date."""
    return str(run_mcp("get_upcoming_followups", {}))


@tool
def send_payment_reminder(
    customer_id: str,
    invoice_id: str,
    message: str,
) -> str:
    """
    Send a payment reminder through the CRM.

    IMPORTANT: This is a real state-changing CRM action, although the project
    is in demo mode. Only call this after the user has explicitly confirmed
    that the reminder should be sent.
    """
    return str(
        run_mcp(
            "send_payment_reminder",
            {
                "customer_id": customer_id,
                "invoice_id": invoice_id,
                "message": message,
            },
        )
    )


@tool
def update_followup(
    customer_id: str,
    invoice_id: str,
    notes: str,
    response_status: str = "noted",
) -> str:
    """Add a follow-up note to the CRM after an interaction."""
    return str(
        run_mcp(
            "update_followup",
            {
                "customer_id": customer_id,
                "invoice_id": invoice_id,
                "notes": notes,
                "response_status": response_status,
            },
        )
    )


TOOLS = [
    get_customers,
    get_customer,
    get_pending_invoices,
    get_overdue_invoices,
    get_customer_invoices,
    get_followup_history,
    get_upcoming_followups,
    send_payment_reminder,
    update_followup,
]

SYSTEM_PROMPT = """
You are a CRM Follow-Up Agent for a fictional company.

Your job is to help an employee inspect customers, invoices, payment status,
follow-up history, and scheduled follow-ups.

IMPORTANT RULES:
1. Use CRM tools for factual customer/invoice information. Never invent CRM data.
2. If a customer name is given but you need an ID, first use get_customers.
3. For payment questions, use invoice tools rather than guessing.
4. For "overdue", use get_overdue_invoices.
5. For "pending/unpaid", use get_pending_invoices.
6. For follow-up history, use get_followup_history.
7. For upcoming follow-ups, use get_upcoming_followups.
8. NEVER send a payment reminder unless the user explicitly asks to send it or
   explicitly confirms after you proposed it.
9. Before sending, make sure you have the correct customer_id and invoice_id.
10. After a successful send, clearly say that this is DEMO MODE and no real
    email was sent.
11. Keep answers concise but useful. Use tables or bullets when helpful.
12. Currency is Indian Rupees (₹) for this demo.
"""


def build_graph():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your .env file before starting the app."
        )

    model = ChatGroq(
        model=MODEL_NAME,
        temperature=0,
    )

    model_with_tools = model.bind_tools(TOOLS)

    def call_model(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(TOOLS, handle_tool_errors=True))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    builder.add_edge("agent", END)

    return builder.compile()


def ask_agent(graph, user_message: str, history: list[dict[str, str]] | None = None) -> str:
    messages = []

    for item in history or []:
        if item["role"] == "user":
            messages.append(("user", item["content"]))
        elif item["role"] == "assistant":
            messages.append(("assistant", item["content"]))

    messages.append(("user", user_message))

    result = graph.invoke({"messages": messages})
    final_message = result["messages"][-1]
    return final_message.content if isinstance(final_message.content, str) else str(final_message.content)