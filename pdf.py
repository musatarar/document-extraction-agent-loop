import base64


def pdf_to_base64(file_path) -> str:
    """Read the PDF at `file_path` and return its contents as a base64 string."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")