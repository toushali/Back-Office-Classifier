import json
import os
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader
from pathlib import Path


def extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a pdf file."""
    reader = PdfReader(str(pdf_path))
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CLASSIFICATION_PROMPT = """You are a back-office document classification assistant. 
Classify the following document into exactly one of these categories:
- Invoice
- Purchase Order
- Contract
- Other

Respond with ONLY valid JSON, no markdown formatting, no code fences, in this exact shape:
{{
  "label": "<one of: Invoice, Purchase Order, Contract, Other>",
  "confidence": <float between 0 and 1>,
  "key_fields": {{
    "vendor_or_party": "<name if found, else null>",
    "amount": "<total amount if found, else null>",
    "date": "<date if found, else null>"
  }},
  "reasoning": "<one sentence explaining the classification>"
}}

Document text:
{document_text}
"""

def classify_document(text: str) -> dict:
    """Send document text to the LLM and return structured classification."""
    prompt = CLASSIFICATION_PROMPT.format(document_text=text[:8000]) #cap length for token safety
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    raw = response.text.strip()
    # strip accidental code fences just in case
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json","",1).strip()

    return json.loads(raw)

ROUTING = {
    "Invoice": "Accounts Payable",
    "Purchase Order": "Procurement",
    "Contract": "Legal",
    "Other": "Manual Review",
}


def route_document(label: str) -> str:
    """Look up the department a classified document should route to."""
    return ROUTING.get(label, "Manual Review")


def process_document(pdf_path: str) -> dict:
    """Full pipeline: extract text, classify, and route a single PDF."""
    text = extract_text(pdf_path)
    result = classify_document(text)
    result["routing_department"] = route_document(result["label"])
    result["source_file"] = str(pdf_path)
    return result