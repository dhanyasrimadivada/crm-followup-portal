from documents.schemas import PurchaseOrderData


def validate_purchase_order(po: PurchaseOrderData):
    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. PO NUMBER
    # ---------------------------------------------------------

    if not po.po_number.strip():
        errors.append("PO number is missing.")

    # ---------------------------------------------------------
    # 2. PO DATE
    # ---------------------------------------------------------

    if not po.po_date.strip():
        errors.append("PO date is missing.")

    # ---------------------------------------------------------
    # 3. CUSTOMER
    # ---------------------------------------------------------

    if not po.customer.company_name.strip():
        errors.append("Customer company name is missing.")

    # ---------------------------------------------------------
    # 4. SUPPLIER
    # ---------------------------------------------------------

    if not po.supplier.company_name.strip():
        errors.append("Supplier company name is missing.")

    # ---------------------------------------------------------
    # 5. TOTAL AMOUNT
    # ---------------------------------------------------------

    if po.amounts.total_amount <= 0:
        errors.append("PO total amount must be greater than zero.")

    # ---------------------------------------------------------
    # 6. PAYMENT TERMS
    # ---------------------------------------------------------

    if po.payment.payment_days < 0:
        errors.append("Payment days cannot be negative.")

    if (
        po.payment.payment_terms
        and po.payment.payment_days == 0
    ):
        warnings.append(
            "Payment terms are present but payment days "
            "could not be extracted."
        )

    # ---------------------------------------------------------
    # 7. ITEMS
    # ---------------------------------------------------------

    if not po.items:
        errors.append("No PO items were extracted.")

    # ---------------------------------------------------------
    # 8. ITEM VALIDATION
    # ---------------------------------------------------------

    for index, item in enumerate(po.items, start=1):

        if not item.item_code.strip():
            warnings.append(
                f"Item {index}: item code is missing."
            )

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

    # ---------------------------------------------------------
    # 9. RETURN RESULT
    # ---------------------------------------------------------

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

    # Load extracted JSON
    with open(
        "po_extracted.json",
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    # Convert JSON → Pydantic object
    po = PurchaseOrderData.model_validate(data)

    # Run business validation
    result = validate_purchase_order(po)

    print("=" * 60)
    print("PURCHASE ORDER VALIDATION")
    print("=" * 60)

    print(
        "Valid:",
        result["valid"]
    )

    print()

    if result["errors"]:

        print("ERRORS:")

        for error in result["errors"]:
            print("-", error)

    else:

        print("Errors: None")

    print()

    if result["warnings"]:

        print("WARNINGS:")

        for warning in result["warnings"]:
            print("-", warning)

    else:

        print("Warnings: None")

    print("=" * 60)