from pydantic import BaseModel, Field
from typing import List


# ============================================================
# CUSTOMER
# ============================================================

class InvoiceCustomerData(BaseModel):
    company_name: str = ""
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    pan: str = ""
    gstin: str = ""
    address: str = ""


# ============================================================
# SUPPLIER
# ============================================================

class InvoiceSupplierData(BaseModel):
    company_name: str = ""
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    pan: str = ""
    gstin: str = ""
    address: str = ""


# ============================================================
# INVOICE ITEM
# ============================================================

class InvoiceItemData(BaseModel):
    description: str = ""
    hsn_code: str = ""
    item_code: str = ""
    quantity: float = 0
    unit_price: float = 0
    line_total: float = 0
    tax_rate: float = 0
    tax_amount: float = 0
    unit: str = ""


# ============================================================
# AMOUNTS
# ============================================================

class InvoiceAmountData(BaseModel):
    subtotal: float = 0
    tax_amount: float = 0
    total_amount: float = 0


# ============================================================
# PAYMENT
# ============================================================

class InvoicePaymentData(BaseModel):
    due_date: str = ""
    payment_days: int = 0
    payment_terms: str = ""


# ============================================================
# REFERENCES
# ============================================================

class InvoiceReferenceData(BaseModel):
    delivery_reference: str = ""
    po_number: str = ""
    quotation_number: str = ""


# ============================================================
# COMPLETE INVOICE
# ============================================================

class InvoiceData(BaseModel):
    invoice_number: str = ""
    invoice_date: str = ""
    document_type: str = ""

    customer: InvoiceCustomerData = Field(
        default_factory=InvoiceCustomerData
    )

    supplier: InvoiceSupplierData = Field(
        default_factory=InvoiceSupplierData
    )

    items: List[InvoiceItemData] = Field(
        default_factory=list
    )

    amounts: InvoiceAmountData = Field(
        default_factory=InvoiceAmountData
    )

    payment: InvoicePaymentData = Field(
        default_factory=InvoicePaymentData
    )

    references: InvoiceReferenceData = Field(
        default_factory=InvoiceReferenceData
    )