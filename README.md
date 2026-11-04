# AI-Powered Insurance Claim Document Processing Pipeline

## 1. Project Overview

This project automates insurance claim document processing using FastAPI, LangGraph, and Google's Gemini API.

A user uploads a single PDF containing multiple document types. The application extracts text, classifies each page, routes relevant pages to specialized extraction agents, and combines the extracted information into structured JSON.

## 2. Architecture

The application follows this LangGraph workflow:

```text
START
  |
  v
Segregator Agent
  |
  +----------+-------------+
  |          |             |
  v          v             v
ID Agent  Discharge Agent  Itemized Bill Agent
  |          |             |
  +----------+-------------+
             |
             v
         Aggregator
             |
             v
            END
```

### Workflow Components

1. **PDF Processor:** Extracts text from every PDF page.
2. **Segregator Agent:** Classifies pages into nine document categories.
3. **ID Agent:** Extracts patient identity and insurance policy information.
4. **Discharge Summary Agent:** Extracts diagnosis, admission and discharge dates, physician, and hospital details.
5. **Itemized Bill Agent:** Extracts bill items and calculates the total using Python.
6. **Aggregator:** Combines all extraction results into one JSON response.
7. **FastAPI:** Exposes the workflow through an HTTP API.

The three extraction agents run in parallel after classification. Each receives only the relevant pages.

## 3. Document Categories

- claim_forms
- cheque_or_bank_details
- identity_document
- itemized_bill
- discharge_summary
- prescription
- investigation_report
- cash_receipt
- other

## 4. Technology Stack

- Python 3.12+
- FastAPI
- LangGraph
- Google Gemini API
- PyMuPDF
- Pydantic
- Uvicorn

## 5. Project Structure

```text
document-processing-pipeline/
├── app/
│   ├── agents/
│   │   ├── aggregator.py
│   │   ├── bill_agent.py
│   │   ├── discharge_agent.py
│   │   ├── id_agent.py
│   │   └── segregator.py
│   ├── services/
│   │   └── pdf_processor.py
│   ├── graph.py
│   └── main.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 6. Installation and Setup

### Prerequisites

- Python 3.12+
- Google Gemini API key

### Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd document-processing-pipeline
```

### Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

```bash
cp .env.example .env
```

Update `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit your actual `.env` file or expose your API key.

## 7. Run the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Application URL:

`http://localhost:8000`

Swagger documentation:

`http://localhost:8000/docs`

Health endpoint:

`http://localhost:8000/health`

## 8. API Usage

### POST /api/process

Accepts an insurance claim PDF.

**Request parameters:**

| Parameter | Type | Description |
|---|---|---|
| claim_id | String | Claim identifier |
| file | PDF | Uploaded claim document |

### Example cURL request

```bash
curl -X POST http://localhost:8000/api/process \
  -F "claim_id=CLAIM-001" \
  -F "file=@sample.pdf"
```

### Response

The API returns JSON containing:

- claim_id
- classifications
- patient_details
- discharge_details
- bill_details

## 9. Testing

The application was tested using an 18-page sample PDF.

Testing included:

- PDF text extraction
- Classification of all 18 pages
- Individual testing of the three extraction agents
- Complete LangGraph workflow execution
- FastAPI health endpoint
- PDF upload using cURL
- PDF upload using Swagger UI

## 10. Current Limitations

- Text extraction currently relies on embedded PDF text. Scanned documents may require OCR or vision-based extraction.
- AI-generated results must be validated against original documents.
- Bill currency and line-item totals must be reconciled against the printed bill before financial use.
- This is a development prototype, not a production-ready system for sensitive medical or insurance information.

## 11. Security

- API credentials are stored in `.env`.
- `.env` and sample PDF files are excluded from Git.
- Production use requires appropriate authentication, authorization, secure storage, and upload limits.

## 12. Author

Developed as an AI-powered document processing pipeline assignment.
