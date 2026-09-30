from datetime import date, timedelta

from database.db import SessionLocal
from database.models import Customer, PurchaseOrder, Invoice


db = SessionLocal()

try:

    customer = db.query(Customer).first()
    po = db.query(PurchaseOrder).first()

    if not customer or not po:
        raise ValueError(
            "Customer or Purchase Order not found."
        )

    invoice = Invoice(
        purchase_order_id=po.id,
        customer_id=customer.id,
        invoice_number="TEST-INV-001",
        invoice_date=date.today() - timedelta(days=40),
        subtotal=100000,
        tax_amount=18000,
        total_amount=118000,
        payment_terms="30 DAYS",
        payment_days=30,
        due_date=date.today() - timedelta(days=10),
        status="PENDING"
    )

    db.add(invoice)
    db.commit()

    print()
    print("=" * 60)
    print("TEST INVOICE CREATED")
    print("=" * 60)
    print(f"Invoice: {invoice.invoice_number}")
    print(f"Amount: ₹{invoice.total_amount}")
    print(f"Due Date: {invoice.due_date}")
    print(f"Status: {invoice.status}")
    print("=" * 60)

finally:
    db.close()