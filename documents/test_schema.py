import json

from documents.schemas import PurchaseOrderData


# Load extracted JSON
with open(
    "po_extracted.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)


# Validate JSON
po = PurchaseOrderData.model_validate(data)


print("=" * 60)
print("JSON VALIDATION SUCCESSFUL")
print("=" * 60)

print("PO Number:", po.po_number)
print("PO Date:", po.po_date)
print("Customer:", po.customer.company_name)
print("Total Amount:", po.amounts.total_amount)
print("Payment Days:", po.payment.payment_days)
print("Items:", len(po.items))

print("=" * 60)