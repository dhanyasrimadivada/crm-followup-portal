from pydantic import BaseModel, Field
from typing import List


class CustomerData(BaseModel):
    company_name: str = ""
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    gstin: str = ""
    pan: str = ""


class SupplierData(BaseModel):
    company_name: str = ""
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    gstin: str = ""
    pan: str = ""


class AmountData(BaseModel):
    subtotal: float = 0
    tax_amount: float = 0
    total_amount: float = 0


class PaymentData(BaseModel):
    payment_terms: str = ""
    payment_days: int = 0


class DeliveryData(BaseModel):
    delivery_terms: str = ""
    delivery_date: str = ""


class POItemData(BaseModel):
    item_code: str = ""
    description: str = ""
    hsn_code: str = ""
    quantity: float = 0
    unit: str = ""
    unit_price: float = 0
    tax_rate: float = 0
    tax_amount: float = 0
    line_total: float = 0


class PurchaseOrderData(BaseModel):
    document_type: str = "Purchase Order"

    po_number: str = ""
    po_date: str = ""

    customer: CustomerData
    supplier: SupplierData

    amounts: AmountData

    payment: PaymentData

    delivery: DeliveryData

    items: List[POItemData] = Field(
        default_factory=list
    )