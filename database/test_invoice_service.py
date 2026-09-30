from documents.invoice_processor import process_invoice
from database.invoice_service import save_invoice


try:

    result = process_invoice(
        "sample_invoice.pdf"
    )

    if not result["success"]:
        print("Invoice processing failed.")
        exit()

    save_invoice(
        result["invoice"],
        "sample_invoice.pdf"
    )

    print()
    print("Invoice database test completed.")

except ValueError as error:

    print()
    print("=" * 60)
    print("INVOICE NOT SAVED")
    print("=" * 60)
    print(f"⚠️ {error}")
    print("=" * 60)