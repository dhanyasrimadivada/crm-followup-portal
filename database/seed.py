import os

from database.db import Base, engine

# Import models so SQLAlchemy knows all the tables
from database.models import (
    Customer,
    Quotation,
    QuotationItem,
    PurchaseOrder,
    PurchaseOrderItem,
    Delivery,
    Invoice,
    Payment,
    FollowUp,
    Document
)


def create_database():

    os.makedirs("data", exist_ok=True)

    Base.metadata.create_all(bind=engine)

    print("CRM database created successfully!")


if __name__ == "__main__":
    create_database()