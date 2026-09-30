import json

from documents.invoice_ocr_service import extract_invoice
from documents.invoice_schemas import InvoiceData
from documents.invoice_validator import validate_invoice


# ============================================================
# PROCESS INVOICE
# ============================================================

def process_invoice(file_path: str):

    print()
    print("=" * 60)
    print("STARTING INVOICE PROCESSING")
    print("=" * 60)

    # --------------------------------------------------------
    # STEP 1: OCR + GROQ EXTRACTION
    # --------------------------------------------------------

    print()
    print("Step 1: Extracting invoice data...")

    extracted_data = extract_invoice(file_path)

    # --------------------------------------------------------
    # STEP 2: PYDANTIC SCHEMA VALIDATION
    # --------------------------------------------------------

    print()
    print("Step 2: Validating invoice schema...")

    invoice = InvoiceData.model_validate(
        extracted_data
    )

    print("Schema validation successful.")

    # --------------------------------------------------------
    # STEP 3: BUSINESS VALIDATION
    # --------------------------------------------------------

    print()
    print("Step 3: Running invoice validation...")

    validation_result = validate_invoice(
        invoice
    )

    # --------------------------------------------------------
    # DISPLAY VALIDATION RESULT
    # --------------------------------------------------------

    if validation_result["errors"]:

        print()
        print("Invoice validation failed.")

        for error in validation_result["errors"]:
            print(f"  ❌ {error}")

        return {
            "success": False,
            "invoice": invoice,
            "validation": validation_result
        }

    print("Invoice validation successful.")

    # --------------------------------------------------------
    # WARNINGS
    # --------------------------------------------------------

    if validation_result["warnings"]:

        print()
        print("Warnings:")

        for warning in validation_result["warnings"]:
            print(f"  ⚠️ {warning}")

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("INVOICE PROCESSING SUCCESSFUL")
    print("=" * 60)

    print(
        f"Invoice Number: "
        f"{invoice.invoice_number}"
    )

    print(
        f"Invoice Date: "
        f"{invoice.invoice_date}"
    )

    print(
        f"PO Number: "
        f"{invoice.references.po_number}"
    )

    print(
        f"Total Amount: "
        f"{invoice.amounts.total_amount}"
    )

    print(
        f"Items: "
        f"{len(invoice.items)}"
    )

    print("=" * 60)

    return {
        "success": True,
        "invoice": invoice,
        "validation": validation_result
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = process_invoice(
        "sample_invoice.pdf"
    )