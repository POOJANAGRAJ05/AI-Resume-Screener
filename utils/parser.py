import io

from PyPDF2 import PdfReader
from docx import Document


def extract_text(file) -> str:
    """Extract text from PDF or DOCX uploaded resume files."""
    file.seek(0)
    raw_bytes = file.read()
    extension = file.name.lower().split(".")[-1]

    if extension == "pdf":
        return extract_text_from_pdf(raw_bytes)
    elif extension == "docx":
        return extract_text_from_docx(raw_bytes)

    raise ValueError("Uploaded file must be a PDF or DOCX resume.")


def extract_text_from_pdf(raw_bytes: bytes) -> str:
    """Parse PDF bytes and return extracted text."""
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


def extract_text_from_docx(raw_bytes: bytes) -> str:
    """Parse DOCX bytes and return extracted text."""
    document = Document(io.BytesIO(raw_bytes))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return "\n".join(paragraphs).strip()
