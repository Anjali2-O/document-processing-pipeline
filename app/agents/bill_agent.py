import json
import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from google import genai

load_dotenv(".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def extract_bill_details(pages: list[dict]) -> dict:
    if not pages:
        return {
            "items": [],
            "calculated_total": "0.00"
        }

    page_content = "\n\n".join(
        f"PAGE {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    prompt = f"""
You are a hospital itemized bill extraction agent.

Extract every bill line item from the supplied documents.

Return valid JSON only in this structure:

{{
    "items": [
        {{
            "description": "Room Charges",
            "quantity": 2,
            "unit_price": "5000.00",
            "total": "10000.00"
        }}
    ],
    "currency": "INR"
}}

Rules:
- Extract all individual bill items.
- Do not include subtotal, tax summary or grand total as line items.
- Preserve the original descriptions.
- Extract quantity, unit price and line-item total when available.
- Use null for unavailable values.
- Do not invent missing information.
- Return valid JSON only.

DOCUMENT PAGES:
{page_content}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    if not response.text:
        raise ValueError("Gemini returned an empty bill extraction response.")

    result = json.loads(response.text)

    # Calculate the grand total using Python.
    calculated_total = Decimal("0.00")

    for item in result.get("items", []):
        line_total = item.get("total")

        if line_total is not None:
            try:
                calculated_total += Decimal(str(line_total))
            except InvalidOperation:
                raise ValueError(
                    f"Invalid bill amount: {line_total}"
                )

    result["calculated_total"] = str(calculated_total.quantize(
        Decimal("0.01")
    ))

    return result
