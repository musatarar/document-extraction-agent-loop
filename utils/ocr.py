import os
from dotenv import load_dotenv
from enum import Enum

import requests

load_dotenv() 

OCR_SPACE_URL = "https://api.ocr.space/parse/image"


class FileType(str, Enum):
    """Top-level MIME types accepted in the base64 data URI."""

    IMAGE = "image"
    APPLICATION = "application"


class FileSubtype(str, Enum):
    """MIME subtypes accepted in the base64 data URI."""

    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    PDF = "pdf"


def _validate(enum_cls, value, name):
    try:
        return enum_cls(value)
    except ValueError:
        valid = ", ".join(m.value for m in enum_cls)
        raise ValueError(f"Invalid {name} {value!r}; expected one of: {valid}") from None


def ocr_base64_image(base64_image, api_key=None, language="eng", file_type=FileType.IMAGE,
                     file_subtype=FileSubtype.JPEG):
    """Send a base64 image to the OCR.space API and return the parsed JSON response.

    The API key is read from the OCR_SPACE_API_KEY environment variable unless
    passed explicitly. `base64_image` is a raw base64 string; it is wrapped in a
    data URI using `file_type` and `file_subtype` (enum members or their string
    values), e.g. "data:image/jpeg;base64,/9j/..." or "data:application/pdf;base64,...".
    """
    api_key = api_key or os.environ.get("OCR_SPACE_API_KEY")
    if not api_key:
        raise ValueError("OCR_SPACE_API_KEY is not set")

    file_type = _validate(FileType, file_type, "file_type")
    file_subtype = _validate(FileSubtype, file_subtype, "file_subtype")
    expected_type = FileType.APPLICATION if file_subtype is FileSubtype.PDF else FileType.IMAGE
    if file_type is not expected_type:
        raise ValueError(
            f"file_subtype {file_subtype.value!r} requires file_type {expected_type.value!r}"
        )

    base64_image = f"data:{file_type.value}/{file_subtype.value};base64,{base64_image}"

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
