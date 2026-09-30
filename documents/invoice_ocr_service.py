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
    raise ValueError(
        "GROQ_API_KEY not found in .env file."
    )

groq_client = Groq(
    api_key=GROQ_API_KEY
)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# INVOICE JSON SCHEMA
# ============================================================

INVOICE_SCHEMA = {

    "type": "object",

    "properties": {

        "document_type": {
            "type": "string"
        },

        "invoice_number": {
            "type": "string"
        },

        "invoice_date": {
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

        "references": {

            "type": "object",

            "properties": {

                "po_number": {
                    "type": "string"
                },

                "quotation_number": {
                    "type": "string"
                },

                "delivery_reference": {
                    "type": "string"
                }
            },

            "required": [
                "po_number",
                "quotation_number",
                "delivery_reference"
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
                },

                "due_date": {
                    "type": "string"
                }
            },

            "required": [
                "payment_terms",
                "payment_days",
                "due_date"
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
        "invoice_number",
        "invoice_date",
        "customer",
        "supplier",
        "references",
        "amounts",
        "payment",
        "items"
    ],

    "additionalProperties": False
}


# ============================================================
# INVOICE EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
You are an intelligent business invoice extraction system.

Read the invoice text carefully and extract ONLY information
that is actually present in the document.

Do NOT invent, guess, estimate, or assume information.

Return ONLY JSON matching the supplied schema.

IMPORTANT RULES:

1. Keep invoice_number exactly as written.

2. Extract invoice_date.

3. Extract customer/buyer information.

4. Extract supplier/seller information.

5. Extract PO number if present.

6. Extract quotation number if present.

7. Extract delivery reference if present.

8. Extract subtotal, tax amount and total amount.

9. Extract payment terms.

10. Extract payment days only when explicitly available.

11. Extract due_date only when explicitly printed.

12. Do not calculate a due date.

13. Extract every invoice line item.

14. Preserve item codes exactly.

15. Preserve HSN/SAC codes exactly.

16. Preserve quantities, units and prices accurately.

17. Extract tax rate and tax amount when available.

18. Extract line total when available.

19. If text information is missing, return "".

20. If numeric information is missing, return 0.

21. If there are no items, return [].

22. Do not treat terms and conditions as line items.

23. Do not invent missing information.

24. The extracted total must be the total stated in the
    invoice, not a newly calculated value.

25. This information will later be validated against the
    Purchase Order by application code.

Return ONLY structured JSON.
"""


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_path: str) -> str:

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Invoice file not found: {file_path}"
        )

    print("Reading invoice PDF...")

    reader = PdfReader(
        str(file_path)
    )

    total_pages = len(reader.pages)

    print(
        f"Total pages: {total_pages}"
    )

    page_texts = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

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

    full_text = "\n".join(
        page_texts
    ).strip()

    if not full_text:

        raise ValueError(
            "No text could be extracted from "
            "the invoice PDF."
        )

    print(
        f"Extracted {len(full_text)} characters "
        f"from {total_pages} pages."
    )

    return full_text


# ============================================================
# EXTRACT INVOICE
# ============================================================

def extract_invoice(file_path: str):

    print()
    print("=" * 60)
    print("STARTING INVOICE EXTRACTION")
    print("=" * 60)

    print(
        f"File: {file_path}"
    )

    # --------------------------------------------------------
    # Extract PDF text locally
    # --------------------------------------------------------

    full_text = extract_pdf_text(
        file_path
    )

    # --------------------------------------------------------
    # Groq extraction
    # --------------------------------------------------------

    print()
    print("Sending invoice text to Groq...")
    print(
        f"Model: {MODEL_NAME}"
    )

    prompt = f"""
{EXTRACTION_PROMPT}

INVOICE TEXT
============

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
                "name": "invoice_extraction",
                "schema": INVOICE_SCHEMA
            }
        },

        temperature=0
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:

        raise ValueError(
            "Groq returned an empty response."
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        if isinstance(content, str):

            data = json.loads(
                content
            )

        else:

            data = content

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Groq returned invalid JSON: {exc}"
        )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    output_file = Path(
        "invoice_extracted.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("INVOICE EXTRACTION SUCCESSFUL")
    print("=" * 60)

    print(
        f"Invoice Number: "
        f"{data.get('invoice_number', '')}"
    )

    print(
        f"Invoice Date: "
        f"{data.get('invoice_date', '')}"
    )

    print(
        f"Customer: "
        f"{data.get('customer', {}).get('company_name', '')}"
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

    extract_invoice(
        "sample_invoice.pdf"
    )