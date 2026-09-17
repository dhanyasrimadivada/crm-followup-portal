from pathlib import Path
import sqlite3
from datetime import date, timedelta

DB_PATH = Path(__file__).parent / "data" / "crm.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            invoice_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE IF NOT EXISTS followups (
            followup_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            invoice_id TEXT,
            followup_date TEXT NOT NULL,
            contact_type TEXT NOT NULL,
            response_status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
        );
        """
    )
    conn.commit()
    conn.close()


def seed_db(force=False):
    init_db()
    conn = get_connection()

    if force:
        conn.executescript(
            """
            DELETE FROM followups;
            DELETE FROM invoices;
            DELETE FROM customers;
            """
        )
        conn.commit()

    count = conn.execute("SELECT COUNT(*) AS n FROM customers").fetchone()["n"]
    if count > 0:
        conn.close()
        return

    today = date.today()

    customers = [
        ("C001", "ABC Technologies", "Ananya Rao", "accounts@abc-tech.example", "+91-9000000001", "active"),
        ("C002", "Nova Systems", "Rahul Mehta", "finance@nova.example", "+91-9000000002", "active"),
        ("C003", "GreenGrid Pvt Ltd", "Priya Sharma", "billing@greengrid.example", "+91-9000000003", "active"),
        ("C004", "TechSphere Solutions", "Vikram Singh", "accounts@techsphere.example", "+91-9000000004", "active"),
        ("C005", "BluePeak Industries", "Neha Kapoor", "finance@bluepeak.example", "+91-9000000005", "inactive"),
    ]

    invoices = [
        ("INV001", "C001", 85000, (today - timedelta(days=60)).isoformat(), (today - timedelta(days=30)).isoformat(), "overdue", "Annual software support"),
        ("INV002", "C002", 32000, (today - timedelta(days=20)).isoformat(), (today + timedelta(days=10)).isoformat(), "pending", "Cloud infrastructure"),
        ("INV003", "C003", 120000, (today - timedelta(days=75)).isoformat(), (today - timedelta(days=45)).isoformat(), "overdue", "Data engineering services"),
        ("INV004", "C001", 45000, (today - timedelta(days=5)).isoformat(), (today + timedelta(days=25)).isoformat(), "pending", "Consulting services"),
        ("INV005", "C004", 67000, (today - timedelta(days=40)).isoformat(), (today - timedelta(days=10)).isoformat(), "overdue", "AI implementation"),
        ("INV006", "C005", 18000, (today - timedelta(days=10)).isoformat(), (today + timedelta(days=20)).isoformat(), "paid", "Maintenance"),
    ]

    followups = [
        ("C001", "INV001", (today - timedelta(days=5)).isoformat(), "email", "no_response", "Payment reminder sent; no response."),
        ("C003", "INV003", (today - timedelta(days=3)).isoformat(), "call", "promised_payment", "Customer promised payment next week."),
        ("C004", "INV005", (today - timedelta(days=7)).isoformat(), "email", "no_response", "Reminder sent; no response."),
        ("C002", "INV002", (today + timedelta(days=3)).isoformat(), "follow_up", "scheduled", "Follow up before invoice due date."),
    ]

    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
        customers,
    )
    conn.executemany(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?)",
        invoices,
    )
    conn.executemany(
        """
        INSERT INTO followups
        (customer_id, invoice_id, followup_date, contact_type, response_status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        followups,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_db(force=True)
    print(f"Database ready: {DB_PATH}")