import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import base64
import io
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def decode_base64(file_base64: str) -> bytes:
    """Decode a base64 string to raw bytes. Raises ValueError on bad input."""
    try:
        # Strip potential data-URI prefix  e.g. "data:application/pdf;base64,..."
        if "," in file_base64:
            file_base64 = file_base64.split(",", 1)[1]
        return base64.b64decode(file_base64)
    except Exception as exc:
        raise ValueError(f"Base64 decoding failed: {exc}") from exc


def extract_from_pdf(raw_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    try:
        import PyPDF2  # noqa: PLC0415

        reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())
        return "\n".join(pages_text)
    except Exception as exc:
        logger.warning("PyPDF2 extraction failed: %s", exc)
        return ""


def extract_from_docx(raw_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    try:
        import docx  # noqa: PLC0415

        document = docx.Document(io.BytesIO(raw_bytes))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as exc:
        logger.warning("python-docx extraction failed: %s", exc)
        return ""


def extract_from_image(raw_bytes: bytes) -> str:
    """Extract text from image bytes using Tesseract OCR via pytesseract."""
    try:
        from PIL import Image  # noqa: PLC0415
        import pytesseract  # noqa: PLC0415

        image = Image.open(io.BytesIO(raw_bytes))
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()
    except Exception as exc:
        logger.warning("OCR extraction failed: %s", exc)
        return ""


def extract_text(file_type: str, file_base64: str) -> Tuple[str, str]:
    """
    Decode base64 input and dispatch to the correct extractor.

    Returns:
        (extracted_text, error_message)  — error_message is empty on success.
    """
    try:
        raw_bytes = decode_base64(file_base64)
    except ValueError as exc:
        return "", str(exc)

    file_type = file_type.lower()

    if file_type == "pdf":
        text = extract_from_pdf(raw_bytes)
    elif file_type == "docx":
        text = extract_from_docx(raw_bytes)
    elif file_type in ("png", "jpg", "jpeg"):
        text = extract_from_image(raw_bytes)
    else:
        return "", f"Unsupported file type: {file_type}"

    if not text.strip():
        return "", "No readable text found in the document."

    return text, ""
