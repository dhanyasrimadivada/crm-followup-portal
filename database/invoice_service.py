from datetime import datetime, timedelta

from database.db import SessionLocal
from database.models import (
    Customer,
    PurchaseOrder,
    Invoice,
    Payment,
    Document
)


# ============================================================
# HELPER
# ============================================================

def parse_date(date_string):

    if not date_string:
        return None

    return datetime.strptime(
        date_string,
        "%Y-%m-%d"
    ).date()


# ============================================================
# SAVE INVOICE
# ============================================================

def save_invoice(
    invoice_data,
    file_path=None
):

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 1. FIND CUSTOMER
        # ----------------------------------------------------

        customer = None

        if invoice_data.customer.gstin:

            customer = db.query(Customer).filter(
                Customer.gstin ==
                invoice_data.customer.gstin
            ).first()

        if not customer:

            customer = db.query(Customer).filter(
                Customer.company_name ==
                invoice_data.customer.company_name
            ).first()

        if not customer:

            customer = Customer(
                company_name=
                    invoice_data.customer.company_name,

                contact_person=
                    invoice_data.customer.contact_person,

                email=
                    invoice_data.customer.email,

                phone=
                    invoice_data.customer.phone,

                address=
                    invoice_data.customer.address,

                gstin=
                    invoice_data.customer.gstin,

                pan=
                    invoice_data.customer.pan
            )

            db.add(customer)
            db.flush()

        # ----------------------------------------------------
        # 2. CHECK DUPLICATE INVOICE
        # ----------------------------------------------------

        existing_invoice = db.query(Invoice).filter(
            Invoice.invoice_number ==
            invoice_data.invoice_number
        ).first()

        if existing_invoice:

            raise ValueError(
                f"Invoice already exists: "
                f"{invoice_data.invoice_number}"
            )

        # ----------------------------------------------------
        # 3. FIND PO
        # ----------------------------------------------------

        po_number = invoice_data.references.po_number

        if not po_number:
            raise ValueError(
            "Invoice cannot be saved because PO number is missing."
    )

        purchase_order = db.query(
            PurchaseOrder
        ).filter(
            PurchaseOrder.po_number == po_number
        ).first()

        if not purchase_order:
            raise ValueError(
            f"PO {po_number} was not found in the database. "
            "Invoice was not saved."
    )

        # ----------------------------------------------------
        # 4. CREATE DOCUMENT RECORD
        # ----------------------------------------------------

        document = Document(
            document_type="INVOICE",
            file_name=(
                file_path.split("\\")[-1]
                if file_path
                else None
            ),
            file_path=file_path,
            customer_id=customer.id,
            processing_status="PROCESSED",
            validation_status="VALID"
        )

        db.add(document)
        db.flush()

        # ----------------------------------------------------
        # 5. CALCULATE DUE DATE
        # ----------------------------------------------------

        invoice_date = parse_date(
            invoice_data.invoice_date
        )

        due_date = parse_date(
            invoice_data.payment.due_date
        )

        if (
            not due_date
            and invoice_date
            and invoice_data.payment.payment_days > 0
        ):

            due_date = (
                invoice_date
                + timedelta(
                    days=
                    invoice_data.payment.payment_days
                )
            )

        # ----------------------------------------------------
        # 6. CREATE INVOICE
        # ----------------------------------------------------

        invoice = Invoice(

            purchase_order_id=(
                purchase_order.id
                if purchase_order
                else None
            ),

            customer_id=customer.id,

            invoice_number=
                invoice_data.invoice_number,

            invoice_date=invoice_date,

            subtotal=
                invoice_data.amounts.subtotal,

            tax_amount=
                invoice_data.amounts.tax_amount,

            total_amount=
                invoice_data.amounts.total_amount,

            payment_terms=
                invoice_data.payment.payment_terms,

            payment_days=
                invoice_data.payment.payment_days,

            due_date=due_date,

            status="PENDING",

            source_document_id=document.id
        )

        db.add(invoice)
        db.flush()

        # ----------------------------------------------------
        # 7. LINK DOCUMENT TO INVOICE
        # ----------------------------------------------------

        document.invoice_id = invoice.id

        # ----------------------------------------------------
        # 8. CREATE PAYMENT RECORD
        # ----------------------------------------------------

        payment = Payment(
            invoice_id=invoice.id,
            amount=0,
            status="PENDING"
        )

        db.add(payment)

        # ----------------------------------------------------
        # 9. SAVE
        # ----------------------------------------------------

        db.commit()

        print()
        print("=" * 60)
        print("INVOICE SAVED SUCCESSFULLY")
        print("=" * 60)

        print(
            f"Invoice ID: {invoice.id}"
        )

        print(
            f"Invoice Number: "
            f"{invoice.invoice_number}"
        )

        print(
            f"Customer: "
            f"{customer.company_name}"
        )

        if purchase_order:

            print(
                f"PO Number: "
                f"{purchase_order.po_number}"
            )

            print(
                f"PO ID: "
                f"{purchase_order.id}"
            )

        else:

            print(
                "PO: Not found"
            )

        print(
            f"Total Amount: "
            f"{invoice.total_amount}"
        )

        print(
            f"Due Date: "
            f"{invoice.due_date}"
        )

        print(
            f"Status: "
            f"{invoice.status}"
        )

        print("=" * 60)

        return invoice

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()