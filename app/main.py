from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.services.pdf_processor import extract_pdf_pages
from app.graph import claim_graph

app = FastAPI(
    title="Document Processing Pipeline",
    description="AI-powered insurance claim document processing",
    version="1.0.0"
)


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
    file: UploadFile = File(...)
):
    if not claim_id.strip():
        raise HTTPException(
            status_code=400,
            detail="claim_id cannot be empty"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    pdf_bytes = await file.read()

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    try:
        pages = extract_pdf_pages(pdf_bytes)

        result = claim_graph.invoke({
            "claim_id": claim_id,
            "pages": pages
        })

        return JSONResponse(
            content=result["final_result"]
        )

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
