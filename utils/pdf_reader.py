import fitz  # PyMuPDF


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Reads a PDF (given as bytes) and returns all its text.
    Raises ValueError with a friendly message if something is wrong.
    """
    # 1) Try to open the file as a PDF
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        raise ValueError(
            "This file could not be opened as a PDF. "
            "Please upload a valid, non-corrupted PDF resume."
        )

    # 2) Password-protected PDFs cannot be read
    if doc.needs_pass:
        doc.close()
        raise ValueError("This PDF is password protected. Please upload an unlocked PDF.")

    if doc.page_count == 0:
        doc.close()
        raise ValueError("This PDF has no pages.")

    # 3) Read the text of every page and join it together
    pages_text = [page.get_text() for page in doc]
    doc.close()
    text = "\n".join(pages_text).strip()

    # 4) Scanned resumes are just pictures, so there is no text to read
    if len(text) < 50:
        raise ValueError(
            "Almost no text was found. Your PDF may be a scanned image. "
            "Please upload a text-based PDF (export it from Word or Google Docs)."
        )

    return text