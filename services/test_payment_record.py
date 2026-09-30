from database.db import SessionLocal
from database.models import Invoice
from services.payment_service import record_payment


db = SessionLocal()

try:
    invoice = db.query(Invoice).filter(
        Invoice.invoice_number == "TEST-INV-001"
    ).first()

    if not invoice:
        raise ValueError("Test invoice not found.")

    invoice_id = invoice.id

    # Reset for payment test
    invoice.status = "PENDING"

    db.commit()

finally:
    db.close()


record_payment(
    invoice_id=invoice_id,
    amount=118000,
    payment_method="Bank Transfer",
    reference_number="TEST-PAY-001",
    notes="Test payment"
)