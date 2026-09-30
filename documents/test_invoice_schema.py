import json

from documents.invoice_schemas import InvoiceData


# ============================================================
# LOAD EXTRACTED INVOICE
# ============================================================

with open(
    "invoice_extracted.json",
    "r",
    encoding="utf-8"
) as file:
    invoice_json = json.load(file)


# ============================================================
# VALIDATE USING PYDANTIC
# ============================================================

invoice = InvoiceData.model_validate(invoice_json)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("=" * 60)
print("INVOICE SCHEMA VALIDATION SUCCESSFUL")
print("=" * 60)

print(f"Invoice Number: {invoice.invoice_number}")
print(f"Invoice Date: {invoice.invoice_date}")

print(
    f"Customer: "
    f"{invoice.customer.company_name}"
)

print(
    f"Supplier: "
    f"{invoice.supplier.company_name}"
)

print(
    f"PO Number: "
    f"{invoice.references.po_number}"
)

print(
    f"Subtotal: "
    f"{invoice.amounts.subtotal}"
)

print(
    f"Tax: "
    f"{invoice.amounts.tax_amount}"
)

print(
    f"Total: "
    f"{invoice.amounts.total_amount}"
)

print(
    f"Items: "
    f"{len(invoice.items)}"
)

print("=" * 60)