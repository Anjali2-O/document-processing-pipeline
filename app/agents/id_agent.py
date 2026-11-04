import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv(".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def extract_id_details(pages: list[dict]) -> dict:
    if not pages:
        return {}

    page_content = "\n\n".join(
        f"PAGE {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    prompt = f"""
You are an insurance claim identity extraction agent.

Extract patient and insurance information from the supplied documents.

Return valid JSON only, using this structure:

{{
    "patient_name": null,
    "date_of_birth": null,
    "id_numbers": [],
    "policy_number": null,
    "insurance_provider": null,
    "member_id": null
}}

Rules:
- Extract only information explicitly present in the documents.
- Do not guess or invent missing values.
- Use null when a single field is unavailable.
- Use an empty list when no ID numbers are available.
- Preserve ID and policy numbers exactly as written.
- Return JSON only.

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
        raise ValueError("Gemini returned an empty ID extraction response.")

    return json.loads(response.text)
