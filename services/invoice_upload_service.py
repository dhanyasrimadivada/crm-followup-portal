from documents.processor import process_invoice
from services.invoice_service import save_invoice_for_po


def upload_invoice_for_po(
    purchase_order_id: int,
    file_path: str,
):
    """
    Complete invoice upload workflow:

    PDF
      ↓
    Groq extraction
      ↓
    Delivery gate
      ↓
    Invoice validation
      ↓
    SQLite
    """

    print()
    print("=" * 60)
    print("INVOICE UPLOAD WORKFLOW")
    print("=" * 60)

    # ==================================================
    # STEP 1: EXTRACT INVOICE
    # ==================================================

    print()
    print("STEP 1: Processing invoice document...")

    invoice_data = process_invoice(file_path)

    if not invoice_data:

        return {
            "success": False,
            "error": "Invoice extraction failed."
        }

    print()
    print("INVOICE EXTRACTION SUCCESSFUL")

    print(
        f"Invoice Number: "
        f"{invoice_data.get('invoice_number')}"
    )

    print(
        f"Invoice Amount: ₹"
        f"{invoice_data.get('amounts', {}).get('total_amount', 0)}"
    )

    # ==================================================
    # STEP 2: SAVE / VALIDATE
    # ==================================================

    print()
    print("STEP 2: Validating invoice workflow...")

    result = save_invoice_for_po(
        purchase_order_id=purchase_order_id,
        invoice_data=invoice_data,
    )

    if not result.get("success"):

        print()
        print("=" * 60)
        print("INVOICE UPLOAD FAILED")
        print("=" * 60)
        print(
            f"❌ {result.get('error')}"
        )
        print("=" * 60)

        return result

    # ==================================================
    # SUCCESS
    # ==================================================

    print()
    print("=" * 60)
    print("INVOICE UPLOAD SUCCESSFUL")
    print("=" * 60)

    print(
        f"Invoice Number: "
        f"{result.get('invoice_number')}"
    )

    print(
        f"Invoice ID: "
        f"{result.get('invoice_id')}"
    )

    print(
        f"PO ID: "
        f"{result.get('purchase_order_id')}"
    )

    print(
        f"Amount: ₹"
        f"{result.get('total_amount')}"
    )

    print(
        f"Due Date: "
        f"{result.get('due_date')}"
    )

    print(
        f"Status: "
        f"{result.get('status')}"
    )

    print("=" * 60)

    return result


if __name__ == "__main__":

    result = upload_invoice_for_po(
        purchase_order_id=1,
        file_path="sample_invoice.pdf",
    )

    print()
    print("FINAL RESULT")
    print(result)