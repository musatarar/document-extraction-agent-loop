import os

import requests

OCR_SPACE_URL = "https://api.ocr.space/parse/image"


def ocr_base64_image(base64_image, api_key=None, language="eng"):
    """Send a base64 image to the OCR.space API and return the parsed JSON response.

    The API key is read from the OCR_SPACE_API_KEY environment variable unless
    passed explicitly. `base64_image` may be a raw base64 string or a full data
    URI (e.g. "data:image/jpeg;base64,/9j/...").
    """
    api_key = api_key or os.environ.get("OCR_SPACE_API_KEY")
    if not api_key:
        raise ValueError("OCR_SPACE_API_KEY is not set")

    if not base64_image.startswith("data:"):
        base64_image = f"data:image/jpeg;base64,{base64_image}"

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
