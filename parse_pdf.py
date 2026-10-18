from utils.ocr import ocr_base64_image, FileType, FileSubtype
from utils.pdf import pdf_to_base64

def parse_pdf(file_path) -> dict:
    """Parse the PDF at `file_path` and return a dictionary of the parsed data."""
    base64_image = pdf_to_base64(file_path)
    response = ocr_base64_image(base64_image, file_type=FileType.APPLICATION, file_subtype=FileSubtype.PDF)
    return response