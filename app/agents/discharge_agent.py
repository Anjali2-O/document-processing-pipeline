import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv(".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def extract_discharge_details(pages: list[dict]) -> dict:
    if not pages:
        return {}

    page_content = "\n\n".join(
        f"PAGE {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    prompt = f"""
You are a medical discharge summary extraction agent.

Extract the following information from the supplied documents.

Return valid JSON only:

{{
    "diagnosis": null,
    "admission_date": null,
    "discharge_date": null,
    "physician_name": null,
    "hospital_name": null
}}

Rules:
- Extract only explicitly available information.
- Never guess or invent missing values.
- Use null for unavailable information.
- Preserve the meaning of the diagnosis.
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
        raise ValueError("Gemini returned an empty discharge extraction response.")

    return json.loads(response.text)
