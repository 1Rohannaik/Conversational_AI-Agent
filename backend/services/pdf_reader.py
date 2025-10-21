from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file path.

    Raises PdfReadError if the file is not a valid PDF or is corrupted.
    Returns an empty string if no text is extractable.
    """
    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text_parts = []
            for page in reader.pages:
                # page.extract_text() can return None
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
            return "\n".join(t for t in text_parts if t)
    except PdfReadError:
        # Bubble up to the API layer for a 4xx response
        raise
    except Exception as exc:
        # Normalize unexpected exceptions to PdfReadError for consistent handling
        raise PdfReadError(str(exc))
