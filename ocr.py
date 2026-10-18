import os
from enum import Enum

import requests

OCR_SPACE_URL = "https://api.ocr.space/parse/image"


class FileType(str, Enum):
    """Top-level MIME types accepted in the base64 data URI."""

    IMAGE = "image"
    APPLICATION = "application"


def ocr_base64_image(base64_image, api_key=None, language="eng", file_type=FileType.IMAGE):
    """Send a base64 image to the OCR.space API and return the parsed JSON response.

    The API key is read from the OCR_SPACE_API_KEY environment variable unless
    passed explicitly. `base64_image` is a raw base64 string; it is wrapped in a
    data URI using `file_type`, a FileType or its string value
    (e.g. "data:image/jpeg;base64,/9j/...").
    """
    api_key = api_key or os.environ.get("OCR_SPACE_API_KEY")
    if not api_key:
        raise ValueError("OCR_SPACE_API_KEY is not set")

    try:
        file_type = FileType(file_type)
    except ValueError:
        valid = ", ".join(t.value for t in FileType)
        raise ValueError(f"Invalid file_type {file_type!r}; expected one of: {valid}") from None

    base64_image = f"data:{file_type.value}/jpeg;base64,{base64_image}"

    # Send as multipart/form-data, matching `curl --form`.
    form = {
        "base64Image": (None, base64_image),
        "language": (None, language),
        "isOverlayRequired": (None, "false"),
    }
    response = requests.post(
        OCR_SPACE_URL,
        headers={"apikey": api_key},
        files=form,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()
