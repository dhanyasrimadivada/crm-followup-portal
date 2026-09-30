from datetime import datetime

from documents.invoice_schemas import InvoiceData


# ============================================================
# VALIDATE INVOICE
# ============================================================

def validate_invoice(invoice: InvoiceData):

    errors = []
    warnings = []

    # --------------------------------------------------------
    # Invoice number
    # --------------------------------------------------------

    if not invoice.invoice_number.strip():
        errors.append("Invoice number is missing.")

    # --------------------------------------------------------
    # Invoice date
    # --------------------------------------------------------

    if not invoice.invoice_date.strip():
        errors.append("Invoice date is missing.")
    else:
        try:
            datetime.strptime(
                invoice.invoice_date,
                "%Y-%m-%d"
            )
        except ValueError:
            errors.append(
                "Invoice date must be in YYYY-MM-DD format."
            )

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    if not invoice.customer.company_name.strip():
        errors.append(
            "Customer company name is missing."
        )

    # --------------------------------------------------------
    # Supplier
    # --------------------------------------------------------

    if not invoice.supplier.company_name.strip():
        errors.append(
            "Supplier company name is missing."
        )

    # --------------------------------------------------------
    # PO reference
    # --------------------------------------------------------

    if not invoice.references.po_number.strip():
        warnings.append(
            "PO number is missing from the invoice."
        )

    # --------------------------------------------------------
    # Amount validation
    # --------------------------------------------------------

    subtotal = invoice.amounts.subtotal
    tax = invoice.amounts.tax_amount
    total = invoice.amounts.total_amount

    if subtotal <= 0:
        errors.append(
            "Invoice subtotal must be greater than zero."
        )

    if total <= 0:
        errors.append(
            "Invoice total must be greater than zero."
        )

    # Check subtotal + tax ≈ total
    calculated_total = subtotal + tax

    if abs(calculated_total - total) > 1:
        errors.append(
            f"Amount mismatch: "
            f"subtotal + tax = {calculated_total}, "
            f"but invoice total = {total}."
        )

    # --------------------------------------------------------
    # Items
    # --------------------------------------------------------

    if not invoice.items:
        errors.append(
            "Invoice contains no items."
        )

    for index, item in enumerate(invoice.items, start=1):

        if not item.description.strip():
            warnings.append(
                f"Item {index}: description is missing."
            )

        if item.quantity <= 0:
            errors.append(
                f"Item {index}: quantity must be greater than zero."
            )

        if item.unit_price < 0:
            errors.append(
                f"Item {index}: unit price cannot be negative."
            )

        if item.line_total < 0:
            errors.append(
                f"Item {index}: line total cannot be negative."
            )

    # --------------------------------------------------------
    # Payment information
    # --------------------------------------------------------

    if not invoice.payment.payment_terms.strip():

        warnings.append(
            "Payment terms are missing from the invoice."
        )

    if invoice.payment.payment_days < 0:

        errors.append(
            "Payment days cannot be negative."
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import json

    # Load extracted invoice
    with open(
        "invoice_extracted.json",
        "r",
        encoding="utf-8"
    ) as file:
        invoice_json = json.load(file)

    # Convert JSON → Pydantic model
    invoice = InvoiceData.model_validate(
        invoice_json
    )

    # Validate
    result = validate_invoice(invoice)

    print()
    print("=" * 60)
    print("INVOICE VALIDATION RESULT")
    print("=" * 60)

    print(
        f"Valid: {result['valid']}"
    )

    print()

    if result["errors"]:

        print("ERRORS:")

        for error in result["errors"]:
            print(f"  ❌ {error}")

    else:

        print("ERRORS:")
        print("  None")

    print()

    if result["warnings"]:

        print("WARNINGS:")

        for warning in result["warnings"]:
            print(f"  ⚠️ {warning}")

    else:

        print("WARNINGS:")
        print("  None")

    print("=" * 60)