import io
from typing import BinaryIO

from PyPDF2 import PdfReader
from docx import Document


def extract_text(file) -> str:
    """Extract plain text from a PDF or DOCX resume file."""
    file.seek(0)
    raw_bytes = file.read()
    file_extension = file.name.lower().split(".")[-1]

    if file_extension == "pdf":
        return extract_text_from_pdf(raw_bytes)
    if file_extension == "docx":
        return extract_text_from_docx(raw_bytes)

    raise ValueError("Unsupported file format. Upload a PDF or DOCX file.")


def extract_text_from_pdf(raw_bytes: bytes) -> str:
    """Extract text from raw PDF bytes using PyPDF2."""
    reader = PdfReader(io.BytesIO(raw_bytes))
    text_chunks = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_chunks.append(page_text)

    return "\n".join(text_chunks).strip()


def extract_text_from_docx(raw_bytes: bytes) -> str:
    """Extract text from raw DOCX bytes using python-docx."""
    document = Document(io.BytesIO(raw_bytes))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return "\n".join(paragraphs).strip()
