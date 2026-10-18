import base64
import io
from pypdf import PdfReader, PdfWriter

def pdf_to_base64(file_path, pages: list[int] | None = None) -> str:
    """Read the PDF at `file_path` and return its contents (optionally only `pages`, 0-indexed) as a base64 string."""
    if pages is None:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")

    reader = PdfReader(file_path)
    writer = PdfWriter()
    n = len(reader.pages)
    for p in pages:
        if not 0 <= p < n:
            raise IndexError(f"page {p} out of range (PDF has {n} pages)")
        writer.add_page(reader.pages[p])

    buf = io.BytesIO()
    writer.write(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")