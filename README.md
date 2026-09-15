# Back Office Document Classification and Routing Agent

TCS APEX Capstone Project 7 — an AI agent that classifies back-office
documents (invoices, purchase orders, contracts) using an LLM, and routes
them to the correct department with confidence scores.

## Problem

Back-office teams handle large volumes of invoices, purchase orders, and
contracts. Manually classifying and routing these documents is slow and
error-prone. This project automates that step.

## Architecture

```
PDF upload → extract_text() → classify_document() [LLM] → route_document() [rule lookup]
                                                         → structured JSON result
```

- **Extraction** (`pypdf`): pulls raw text from an uploaded PDF.
- **Classification** (Gemini API): classifies the document as Invoice,
  Purchase Order, Contract, or Other, with a confidence score, extracted
  key fields, and a one-line reasoning explanation — all returned as
  structured JSON.
- **Routing**: a deterministic lookup table, not an LLM call, so routing
  decisions are consistent and auditable.

## Setup

```powershell
uv sync
uv add google-genai pypdf streamlit python-dotenv
```

Copy `.env.example` to `.env` and add your Gemini API key
(get one free at https://aistudio.google.com/apikey):

```
GEMINI_API_KEY=your_key_here
```

## Usage

**CLI — single file:**
```powershell
uv run main.py classify sample/invoice_1.pdf
```

**CLI — batch (whole folder):**
```powershell
uv run main.py classify sample --batch
```

**Web UI:**
```powershell
uv run streamlit run streamlit_app.py
```
Then open `http://localhost:8501` and upload a PDF.

## Tests

```powershell
uv run pytest -v
```

## Example output

```json
{
  "label": "Invoice",
  "confidence": 0.95,
  "key_fields": {
    "vendor_or_party": "Acme Supplies Ltd.",
    "amount": "$4,250.00",
    "date": "2026-08-12"
  },
  "reasoning": "Document contains itemized charges, a total due, and payment terms typical of an invoice.",
  "routing_department": "Accounts Payable",
  "source_file": "sample/invoice_1.pdf"
}
```

## Limitations

- Text-based PDFs only — no OCR for scanned/image documents.
- Routing rules are fixed; adding a new document category requires a
  code change, not just a config change.

## Tech stack

Python, uv, Google Gemini API, Streamlit, pypdf, pytest.