from pathlib import Path

from documents.ocr_service import extract_purchase_order
from documents.invoice_ocr_service import extract_invoice


def process_purchase_order(file_path: str):
    """
    Process a Purchase Order using:
    PDF → pypdf → Groq → structured JSON
    """
    print("Processing Purchase Order...")

    data = extract_purchase_order(file_path)

    if not data:
        raise ValueError(
            "Purchase Order extraction returned no data."
        )

    return data


def process_invoice(file_path: str):
    """
    Process an Invoice using:
    PDF → pypdf → Groq → structured JSON
    """
    print("Processing Invoice...")

    data = extract_invoice(file_path)

    if not data:
        raise ValueError(
            "Invoice extraction returned no data."
        )

    return data


if __name__ == "__main__":

    print("=" * 60)
    print("DOCUMENT PROCESSOR")
    print("=" * 60)

    po_file = "sample_po.pdf"

    invoice_file = "sample_invoice.pdf"

    print("\nProcessing PO...")
    po_data = process_purchase_order(po_file)

    print("\nProcessing Invoice...")
    invoice_data = process_invoice(invoice_file)

    print("\n" + "=" * 60)
    print("ALL DOCUMENTS PROCESSED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"PO Number: "
        f"{po_data.get('po_number', '')}"
    )

    print(
        f"Invoice Number: "
        f"{invoice_data.get('invoice_number', '')}"
    )