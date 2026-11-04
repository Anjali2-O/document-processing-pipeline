
import os
import secrets

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.responses import JSONResponse

from app.services.pdf_processor import extract_pdf_pages
from app.graph import claim_graph

app = FastAPI(
    title="Document Processing Pipeline",
    description="AI-powered insurance claim document processing",
    version="1.0.0"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/")
def home():
    return {
        "message": "Document Processing Pipeline API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/process")
async def process_claim(
    claim_id: str = Form(...),
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    try:
        # 1. Authenticate the API request
        expected_api_key = os.getenv("API_ACCESS_KEY")

        if not expected_api_key:
            raise HTTPException(
                status_code=503,
                detail="API authentication is not configured"
            )

        if not x_api_key or not secrets.compare_digest(
            x_api_key, expected_api_key
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )

        # 2. Validate claim ID
        if not claim_id.strip():
            raise HTTPException(
                status_code=400,
                detail="claim_id cannot be empty"
            )

        # 3. Validate file extension
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted"
            )

        # 4. Read at most 10 MB + 1 byte
        pdf_bytes = await file.read(MAX_FILE_SIZE + 1)

        if len(pdf_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF file exceeds the 10 MB limit"
            )

        # 5. Validate PDF signature
        if not pdf_bytes.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )

        # 6. Extract PDF pages
        pages = extract_pdf_pages(pdf_bytes)

        # 7. Execute LangGraph workflow
        result = claim_graph.invoke({
            "claim_id": claim_id,
            "pages": pages
        })

        return JSONResponse(
            content=result["final_result"]
        )

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        ) from error

    finally:
        await file.close()
