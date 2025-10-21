from db.base import Base  # re-export Base for convenience
from .pdf import PDFFile  # ensure model is imported so metadata is populated

__all__ = ["Base", "PDFFile"]
