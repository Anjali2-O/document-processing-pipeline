import pymupdf as fitz


def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    """Extract text from every PDF page while preserving page numbers."""

    pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        if document.page_count == 0:
            raise ValueError("The uploaded PDF contains no pages.")

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            pages.append({
                "page_number": page_number,
                "text": text
            })

    return pages
