from database.db import SessionLocal
from database.models import Quotation, PurchaseOrder

from documents.processor import process_purchase_order
from database.po_service import save_purchase_order
from services.po_validation_service import validate_po_against_quotation


def upload_po_for_quotation(
    quotation_id: int,
    file_path: str
):
    """
    Complete PO workflow:

    Accepted Quotation
        ↓
    Upload PO
        ↓
    pypdf → Groq extraction
        ↓
    Validate PO against quotation
        ↓
    If valid → Save PO
        ↓
    Link PO to quotation
        ↓
    Quotation = WON

    If validation fails:
        PO is NOT saved.
    """

    db = SessionLocal()

    try:

        # ==================================================
        # 1. FIND QUOTATION
        # ==================================================

        quotation = (
            db.query(Quotation)
            .filter(
                Quotation.id == quotation_id
            )
            .first()
        )

        if quotation is None:
            raise ValueError(
                f"Quotation {quotation_id} not found."
            )

        # ==================================================
        # 2. CHECK QUOTATION STATUS
        # ==================================================

        if quotation.status not in (
            "ACCEPTED",
            "AWAITING_PO",
            "WON"
        ):
            raise ValueError(
                "PO upload is allowed only after "
                "quotation acceptance."
            )

        print()
        print("=" * 60)
        print("PO UPLOAD WORKFLOW")
        print("=" * 60)

        print(
            f"Quotation: "
            f"{quotation.quotation_number}"
        )

        print(
            f"Customer: "
            f"{quotation.customer.company_name}"
        )

        print(
            f"Quotation Amount: "
            f"₹{quotation.total_amount}"
        )

        print("=" * 60)

        # ==================================================
        # 3. EXTRACT PO
        # ==================================================

        print()
        print("STEP 1: Processing PO document...")

        purchase_order_data = (
            process_purchase_order(file_path)
        )

        po_number = (
            purchase_order_data
            .get("po_number", "")
        )

        po_amount = float(
            purchase_order_data
            .get("amounts", {})
            .get("total_amount", 0)
            or 0
        )

        print()
        print("PO EXTRACTION SUCCESSFUL")

        print(
            f"PO Number: {po_number}"
        )

        print(
            f"PO Amount: ₹{po_amount}"
        )

        # ==================================================
        # 4. VALIDATE PO AGAINST QUOTATION
        # ==================================================

        print()
        print(
            "STEP 2: Validating PO against quotation..."
        )

        validation = (
            validate_po_against_quotation(
                quotation_id=quotation_id,
                po_data=purchase_order_data
            )
        )

        # ==================================================
        # 5. REJECT IF VALIDATION FAILS
        # ==================================================

        if not validation["valid"]:

            print()
            print("=" * 60)
            print("PO VALIDATION FAILED")
            print("=" * 60)

            for error in validation["errors"]:
                print(f"❌ {error}")

            print("=" * 60)

            return {
                "success": False,
                "quotation_id": quotation.id,
                "quotation_number": (
                    quotation.quotation_number
                ),
                "po_number": po_number,
                "quotation_amount": (
                    quotation.total_amount
                ),
                "po_amount": po_amount,
                "status": "REJECTED",
                "errors": validation["errors"]
            }

        # ==================================================
        # 6. VALIDATION PASSED
        # ==================================================

        print()
        print("=" * 60)
        print("PO VALIDATION PASSED")
        print("=" * 60)

        print(
            "✓ Amount matched"
        )

        print(
            "✓ Customer matched"
        )

        print(
            "✓ Items validated"
        )

        print("=" * 60)

        # ==================================================
        # 7. SAVE PO
        # ==================================================

        print()
        print("STEP 3: Saving PO to database...")

        try:

            save_purchase_order(
                purchase_order_data,
                file_path,
                quotation_id=quotation_id
            )

        except ValueError as e:

            if "already exists in the database" not in str(e):
                raise

            print(
                "PO already exists. "
                "Using existing PO record."
            )

        # ==================================================
        # 8. FIND SAVED PO
        # ==================================================

        purchase_order = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.po_number
                == po_number
            )
            .first()
        )

        if purchase_order is None:

            raise ValueError(
                "PO was saved but could not be "
                "found for quotation linking."
            )

        # ==================================================
        # 9. LINK PO TO QUOTATION
        # ==================================================

        purchase_order.quotation_id = quotation.id

        # ==================================================
        # 10. UPDATE QUOTATION STATUS
        # ==================================================

        quotation.status = "WON"

        db.commit()

        # ==================================================
        # 11. SUCCESS
        # ==================================================

        print()
        print("=" * 60)
        print("PO UPLOAD SUCCESSFUL")
        print("=" * 60)

        print(
            f"Quotation: "
            f"{quotation.quotation_number}"
        )

        print(
            f"PO Number: "
            f"{purchase_order.po_number}"
        )

        print(
            f"PO ID: "
            f"{purchase_order.id}"
        )

        print(
            f"Quotation Status: "
            f"{quotation.status}"
        )

        print("=" * 60)

        return {
            "success": True,
            "quotation_id": quotation.id,
            "quotation_number": (
                quotation.quotation_number
            ),
            "purchase_order_id": (
                purchase_order.id
            ),
            "po_number": (
                purchase_order.po_number
            ),
            "quotation_amount": (
                quotation.total_amount
            ),
            "po_amount": po_amount,
            "status": quotation.status,
            "validation": {
                "valid": True,
                "errors": []
            }
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = upload_po_for_quotation(
        quotation_id=2,
        file_path="sample_po.pdf"
    )

    print()
    print("FINAL RESULT")
    print(result)