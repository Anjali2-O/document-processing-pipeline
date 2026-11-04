import json
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = [
    "claim_forms",
    "cheque_or_bank_details",
    "identity_document",
    "itemized_bill",
    "discharge_summary",
    "prescription",
    "investigation_report",
    "cash_receipt",
    "other",
]

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def segregate_pages(pages: list[dict]) -> list[dict]:
    page_content = "\n\n".join(
        f"PAGE {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    prompt = f"""
You are a document classification agent.

Classify every supplied PDF page into exactly one of these categories:
{json.dumps(CATEGORIES)}

Rules:
- Classify each page independently.
- Return every page exactly once.
- Never invent page numbers.
- If a page does not match another category, use other.
- Return valid JSON only.

Expected JSON:
{{
  "classifications": [
    {{"page_number": 1, "category": "claim_forms"}}
  ]
}}

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

    result = json.loads(response.text)
    classifications = result["classifications"]

    expected_pages = {p["page_number"] for p in pages}
    actual_pages = [item["page_number"] for item in classifications]

    if set(actual_pages) != expected_pages or len(actual_pages) != len(expected_pages):
        raise ValueError("Gemini returned missing or duplicate page classifications.")

    for item in classifications:
        if item["category"] not in CATEGORIES:
            raise ValueError(f"Invalid document category: {item['category']}")

    return sorted(classifications, key=lambda x: x["page_number"])
