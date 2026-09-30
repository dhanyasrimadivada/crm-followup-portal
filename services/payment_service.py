from datetime import date, datetime

from database.db import SessionLocal
from database.models import Invoice, Payment


def get_payment_for_invoice(invoice_id: int):
    db = SessionLocal()

    try:
        payment = (
            db.query(Payment)
            .filter(Payment.invoice_id == invoice_id)
            .order_by(Payment.id.desc())
            .first()
        )

        if payment is None:
            return {
                "success": True,
                "invoice_id": invoice_id,
                "status": "PENDING",
                "payment": None,
            }

        return {
            "success": True,
            "invoice_id": invoice_id,
            "payment_id": payment.id,
            "amount": payment.amount,
            "payment_date": (
                str(payment.payment_date)
                if payment.payment_date
                else None
            ),
            "payment_method": payment.payment_method,
            "reference_number": payment.reference_number,
            "status": payment.status,
            "notes": payment.notes,
        }

    finally:
        db.close()


def get_overdue_invoices():
    """Get all invoices that currently have OVERDUE status."""
    db = SessionLocal()
    try:
        return (
            db.query(Invoice)
            .filter(Invoice.status == "OVERDUE")
            .all()
        )
    finally:
        db.close()


def record_payment(
    invoice_id: int,
    status: str = "PAID",
    amount=None,
    payment_date=None,
    payment_method=None,
    reference_number=None,
    notes=None,
):
    """
    Explicitly record whether an invoice was paid.

    PAID:
        Invoice becomes PAID and will never automatically
        become OVERDUE.

    NOT_PAID:
        Invoice remains PENDING unless an actual due date
        exists and has passed.
    """

    db = SessionLocal()

    try:

        # ==================================================
        # FIND INVOICE
        # ==================================================

        invoice = (
            db.query(Invoice)
            .filter(Invoice.id == invoice_id)
            .first()
        )

        if invoice is None:
            return {
                "success": False,
                "error": "Invoice not found."
            }

        # ==================================================
        # NORMALIZE STATUS
        # ==================================================

        status = str(status).strip().upper()

        if status in ("NOT PAID", "NOT_PAID", "UNPAID"):
            status = "NOT_PAID"

        elif status == "PAID":
            status = "PAID"

        else:
            return {
                "success": False,
                "error": (
                    "Payment status must be "
                    "PAID or NOT PAID."
                )
            }

        # ==================================================
        # PAID
        # ==================================================

        if status == "PAID":

            if payment_date is None:
                payment_date = date.today()

            elif isinstance(payment_date, str):

                parsed_date = None

                for fmt in (
                    "%Y-%m-%d",
                    "%d/%m/%Y",
                    "%d-%m-%Y",
                ):

                    try:
                        parsed_date = datetime.strptime(
                            payment_date,
                            fmt
                        ).date()
                        break

                    except ValueError:
                        continue

                payment_date = parsed_date

            payment_amount = (
                float(amount)
                if amount is not None
                else float(invoice.total_amount or 0)
            )

            payment = Payment(
                invoice_id=invoice.id,
                amount=payment_amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference_number=reference_number,
                status="PAID",
                notes=notes,
            )

            db.add(payment)

            # IMPORTANT:
            # Once paid, invoice stays PAID.

            invoice.status = "PAID"

            db.commit()
            db.refresh(payment)

            return {
                "success": True,
                "invoice_id": invoice.id,
                "payment_id": payment.id,
                "status": "PAID",
                "invoice_status": "PAID",
                "amount": payment.amount,
                "payment_date": (
                    str(payment.payment_date)
                    if payment.payment_date
                    else None
                ),
            }

        # ==================================================
        # NOT PAID
        # ==================================================

        if status == "NOT_PAID":

            # Do not create a fake payment record.
            # Determine invoice status from the actual
            # due date if one exists.

            today = date.today()

            if invoice.due_date:

                if invoice.due_date < today:

                    invoice.status = "OVERDUE"

                else:

                    invoice.status = "PENDING"

            else:

                # No due date means we cannot call it overdue.

                invoice.status = "PENDING"

            db.commit()

            return {
                "success": True,
                "invoice_id": invoice.id,
                "status": "NOT_PAID",
                "invoice_status": invoice.status,
                "due_date": (
                    str(invoice.due_date)
                    if invoice.due_date
                    else None
                ),
            }

    except Exception:

        db.rollback()
        raise

    finally:
        db.close()