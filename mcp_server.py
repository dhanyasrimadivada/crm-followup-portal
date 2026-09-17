from datetime import date
from typing import Any

from mcp.server import MCPServer

from db import get_connection, init_db, seed_db

mcp = MCPServer(
    "CRM Follow-Up Server",
    instructions=(
        "This server provides customer, invoice, follow-up, and reminder "
        "tools for a demonstration CRM application."
    ),
)


def rows_to_dict(rows) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


@mcp.tool()
def get_customers(search: str = "") -> list[dict[str, Any]]:
    """Find customers by company name, contact name, or email."""
    conn = get_connection()
    like = f"%{search.strip()}%"
    rows = conn.execute(
        """
        SELECT customer_id, company_name, contact_name, email, phone, status
        FROM customers
        WHERE company_name LIKE ?
           OR contact_name LIKE ?
           OR email LIKE ?
        ORDER BY company_name
        """,
        (like, like, like),
    ).fetchall()
    conn.close()
    return rows_to_dict(rows)


@mcp.tool()
def get_customer(customer_id: str) -> dict[str, Any]:
    """Get complete information for one customer using the customer ID."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT customer_id, company_name, contact_name, email, phone, status
        FROM customers
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()
    conn.close()

    if not row:
        return {"error": f"Customer {customer_id} was not found."}
    return dict(row)


@mcp.tool()
def get_pending_invoices() -> list[dict[str, Any]]:
    """Get all unpaid invoices, including both pending and overdue invoices."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            i.invoice_id,
            i.customer_id,
            c.company_name,
            c.email,
            i.amount,
            i.invoice_date,
            i.due_date,
            i.status,
            i.description
        FROM invoices i
        JOIN customers c ON c.customer_id = i.customer_id
        WHERE i.status IN ('pending', 'overdue')
        ORDER BY i.due_date ASC
        """
    ).fetchall()
    conn.close()
    return rows_to_dict(rows)


@mcp.tool()
def get_overdue_invoices() -> list[dict[str, Any]]:
    """Get invoices whose status is overdue, including days overdue."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            i.invoice_id,
            i.customer_id,
            c.company_name,
            c.contact_name,
            c.email,
            i.amount,
            i.invoice_date,
            i.due_date,
            i.status,
            i.description
        FROM invoices i
        JOIN customers c ON c.customer_id = i.customer_id
        WHERE i.status = 'overdue'
        ORDER BY i.due_date ASC
        """
    ).fetchall()
    conn.close()

    result = []
    today = date.today()
    for row in rows:
        item = dict(row)
        due = date.fromisoformat(item["due_date"])
        item["days_overdue"] = max((today - due).days, 0)
        result.append(item)
    return result


@mcp.tool()
def get_customer_invoices(customer_id: str) -> list[dict[str, Any]]:
    """Get all invoices belonging to a customer."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT invoice_id, customer_id, amount, invoice_date, due_date,
               status, description
        FROM invoices
        WHERE customer_id = ?
        ORDER BY due_date DESC
        """,
        (customer_id,),
    ).fetchall()
    conn.close()
    return rows_to_dict(rows)


@mcp.tool()
def get_followup_history(customer_id: str) -> list[dict[str, Any]]:
    """Get the follow-up/contact history for a customer."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            f.followup_id,
            f.customer_id,
            f.invoice_id,
            c.company_name,
            f.followup_date,
            f.contact_type,
            f.response_status,
            f.notes
        FROM followups f
        JOIN customers c ON c.customer_id = f.customer_id
        WHERE f.customer_id = ?
        ORDER BY f.followup_date DESC
        """,
        (customer_id,),
    ).fetchall()
    conn.close()
    return rows_to_dict(rows)


@mcp.tool()
def get_upcoming_followups() -> list[dict[str, Any]]:
    """Get follow-ups scheduled for today or a future date."""
    conn = get_connection()
    today = date.today().isoformat()
    rows = conn.execute(
        """
        SELECT
            f.followup_id,
            f.customer_id,
            f.invoice_id,
            c.company_name,
            c.email,
            f.followup_date,
            f.contact_type,
            f.response_status,
            f.notes
        FROM followups f
        JOIN customers c ON c.customer_id = f.customer_id
        WHERE f.followup_date >= ?
        ORDER BY f.followup_date ASC
        """,
        (today,),
    ).fetchall()
    conn.close()
    return rows_to_dict(rows)


@mcp.tool()
def send_payment_reminder(
    customer_id: str,
    invoice_id: str,
    message: str,
) -> dict[str, Any]:
    """
    Simulate sending a payment reminder.

    This is a demo-safe mock email action. It does not send a real email.
    The agent should only call this after the user explicitly confirms that
    the reminder should be sent.
    """
    conn = get_connection()

    customer = conn.execute(
        "SELECT company_name, email FROM customers WHERE customer_id = ?",
        (customer_id,),
    ).fetchone()

    invoice = conn.execute(
        """
        SELECT invoice_id, amount, due_date, status
        FROM invoices
        WHERE invoice_id = ? AND customer_id = ?
        """,
        (invoice_id, customer_id),
    ).fetchone()

    if not customer:
        conn.close()
        return {"success": False, "error": "Customer not found."}

    if not invoice:
        conn.close()
        return {"success": False, "error": "Invoice not found for this customer."}

    if invoice["status"] == "paid":
        conn.close()
        return {"success": False, "error": "This invoice is already marked as paid."}

    today = date.today().isoformat()

    conn.execute(
        """
        INSERT INTO followups
        (customer_id, invoice_id, followup_date, contact_type, response_status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            customer_id,
            invoice_id,
            today,
            "email",
            "sent",
            f"Demo reminder sent: {message}",
        ),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "action": "payment_reminder_sent",
        "recipient": customer["email"],
        "company_name": customer["company_name"],
        "invoice_id": invoice_id,
        "amount": invoice["amount"],
        "message": message,
        "note": "DEMO MODE: no real email was sent.",
    }


@mcp.tool()
def update_followup(
    customer_id: str,
    invoice_id: str,
    notes: str,
    response_status: str = "noted",
) -> dict[str, Any]:
    """Add a CRM follow-up note after an interaction."""
    conn = get_connection()
    today = date.today().isoformat()

    conn.execute(
        """
        INSERT INTO followups
        (customer_id, invoice_id, followup_date, contact_type, response_status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (customer_id, invoice_id, today, "crm_note", response_status, notes),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "CRM follow-up record updated.",
        "customer_id": customer_id,
        "invoice_id": invoice_id,
    }


if __name__ == "__main__":
    init_db()
    seed_db()
    # MCP v2 uses MCPServer. Streamable HTTP exposes the server at /mcp.
    mcp.run(transport="streamable-http")