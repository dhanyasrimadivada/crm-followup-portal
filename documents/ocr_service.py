import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file.")

groq_client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# PO JSON SCHEMA
# ============================================================

json_schema = {
    "type": "object",

    "properties": {

        "document_type": {
            "type": "string"
        },

        "po_number": {
            "type": "string"
        },

        "po_date": {
            "type": "string"
        },

        "customer": {
            "type": "object",

            "properties": {

                "company_name": {
                    "type": "string"
                },

                "contact_person": {
                    "type": "string"
                },

                "email": {
                    "type": "string"
                },

                "phone": {
                    "type": "string"
                },

                "address": {
                    "type": "string"
                },

                "gstin": {
                    "type": "string"
                },

                "pan": {
                    "type": "string"
                }
            },

            "required": [
                "company_name",
                "contact_person",
                "email",
                "phone",
                "address",
                "gstin",
                "pan"
            ],

            "additionalProperties": False
        },

        "supplier": {
            "type": "object",

            "properties": {

                "company_name": {
                    "type": "string"
                },

                "contact_person": {
                    "type": "string"
                },

                "email": {
                    "type": "string"
                },

                "phone": {
                    "type": "string"
                },

                "gstin": {
                    "type": "string"
                },

                "pan": {
                    "type": "string"
                }
            },

            "required": [
                "company_name",
                "contact_person",
                "email",
                "phone",
                "gstin",
                "pan"
            ],

            "additionalProperties": False
        },

        "amounts": {
            "type": "object",

            "properties": {

                "subtotal": {
                    "type": "number"
                },

                "tax_amount": {
                    "type": "number"
                },

                "total_amount": {
                    "type": "number"
                }
            },

            "required": [
                "subtotal",
                "tax_amount",
                "total_amount"
            ],

            "additionalProperties": False
        },

        "payment": {
            "type": "object",

            "properties": {

                "payment_terms": {
                    "type": "string"
                },

                "payment_days": {
                    "type": "integer"
                }
            },

            "required": [
                "payment_terms",
                "payment_days"
            ],

            "additionalProperties": False
        },

        "delivery": {
            "type": "object",

            "properties": {

                "delivery_terms": {
                    "type": "string"
                },

                "delivery_date": {
                    "type": "string"
                }
            },

            "required": [
                "delivery_terms",
                "delivery_date"
            ],

            "additionalProperties": False
        },

        "items": {
            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "item_code": {
                        "type": "string"
                    },

                    "description": {
                        "type": "string"
                    },

                    "hsn_code": {
                        "type": "string"
                    },

                    "quantity": {
                        "type": "number"
                    },

                    "unit": {
                        "type": "string"
                    },

                    "unit_price": {
                        "type": "number"
                    },

                    "tax_rate": {
                        "type": "number"
                    },

                    "tax_amount": {
                        "type": "number"
                    },

                    "line_total": {
                        "type": "number"
                    }
                },

                "required": [
                    "item_code",
                    "description",
                    "hsn_code",
                    "quantity",
                    "unit",
                    "unit_price",
                    "tax_rate",
                    "tax_amount",
                    "line_total"
                ],

                "additionalProperties": False
            }
        }
    },

    "required": [
        "document_type",
        "po_number",
        "po_date",
        "customer",
        "supplier",
        "amounts",
        "payment",
        "delivery",
        "items"
    ],

    "additionalProperties": False
}


# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
You are an intelligent Purchase Order document extraction system.

Read the supplied Purchase Order text carefully and extract
ONLY information that is actually present in the document.

Do NOT invent, assume, estimate, or guess information.

Return ONLY JSON matching the supplied schema.

IMPORTANT RULES:

1. Extract the PO number exactly as written.

2. Extract the PO date.

3. Identify the BUYER / CUSTOMER correctly.

4. Identify the SUPPLIER / VENDOR correctly.

5. Do not confuse buyer and supplier.

6. Extract subtotal, tax amount and total amount.

7. Extract payment terms.

8. If payment days are explicitly mentioned, extract the number.
   Otherwise return 0.

9. Do not calculate a payment due date.

10. Extract delivery terms and delivery date if present.

11. Extract EVERY actual line item.

12. Do not treat terms and conditions as line items.

13. Preserve item codes exactly.

14. Preserve HSN/SAC codes exactly.

15. Preserve quantities and unit prices accurately.

16. Extract tax rate and tax amount when available.

17. Extract line totals when available.

18. If a text field is missing, return "".

19. If a numeric field is missing, return 0.

20. If there are no line items, return [].

21. Do not create information that does not exist in the document.

22. The extracted total must come from the document.
    Do not calculate or replace it with your own calculation.

23. This extraction will later be validated against the
    accepted quotation by application code.

Return ONLY the structured JSON.
"""


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_path: str) -> str:

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Purchase Order file not found: {file_path}"
        )

    print("Reading Purchase Order PDF...")

    reader = PdfReader(str(file_path))

    total_pages = len(reader.pages)

    print(f"Total pages: {total_pages}")

    page_texts = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text() or ""
        except Exception as exc:
            print(
                f"Warning: Could not extract page "
                f"{page_number}: {exc}"
            )
            text = ""

        if text.strip():
            page_texts.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

    full_text = "\n".join(page_texts).strip()

    if not full_text:
        raise ValueError(
            "No text could be extracted from the Purchase Order PDF."
        )

    print(
        f"Extracted {len(full_text)} characters "
        f"from {total_pages} pages."
    )

    return full_text


# ============================================================
# GROQ STRUCTURED EXTRACTION
# ============================================================

def extract_purchase_order(file_path: str):

    print()
    print("=" * 60)
    print("STARTING PURCHASE ORDER EXTRACTION")
    print("=" * 60)

    print(f"File: {file_path}")

    # --------------------------------------------------------
    # Extract text locally
    # --------------------------------------------------------

    full_text = extract_pdf_text(file_path)

    # --------------------------------------------------------
    # Send text to Groq
    # --------------------------------------------------------

    print()
    print("Sending extracted PO text to Groq...")
    print(f"Model: {MODEL_NAME}")

    prompt = f"""
{EXTRACTION_PROMPT}

PURCHASE ORDER TEXT
===================

{full_text}
"""

    response = groq_client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_schema",

            "json_schema": {
                "name": "purchase_order_extraction",
                "schema": json_schema
            }
        },

        temperature=0
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Groq returned an empty response."
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Groq returned invalid JSON: {exc}"
        )

    # --------------------------------------------------------
    # Save extracted JSON
    # --------------------------------------------------------

    output_file = Path("po_extracted.json")

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("PURCHASE ORDER EXTRACTION SUCCESSFUL")
    print("=" * 60)

    print(
        f"PO Number: "
        f"{data.get('po_number', '')}"
    )

    print(
        f"PO Date: "
        f"{data.get('po_date', '')}"
    )

    print(
        f"Customer: "
        f"{data.get('customer', {}).get('company_name', '')}"
    )

    print(
        f"Supplier: "
        f"{data.get('supplier', {}).get('company_name', '')}"
    )

    print(
        f"Total Amount: "
        f"{data.get('amounts', {}).get('total_amount', 0)}"
    )

    print(
        f"Items: "
        f"{len(data.get('items', []))}"
    )

    print(
        f"JSON file: {output_file}"
    )

    print("=" * 60)

    return data


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    extract_purchase_order(
        "sample_po.pdf"
    )