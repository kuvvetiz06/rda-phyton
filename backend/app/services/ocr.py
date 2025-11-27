import io
from typing import List, Optional

import numpy as np
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes
from PIL import Image


# Initialize the OCR model once to reuse across requests.
ocr_model = PaddleOCR(use_angle_cls=True, lang="en")


def _extract_text_from_image(image: Image.Image) -> str:
    """Run PaddleOCR on a PIL image and return concatenated text."""

    # PaddleOCR expects RGB numpy arrays
    if image.mode != "RGB":
        image = image.convert("RGB")
    np_image = np.array(image)

    results = ocr_model.ocr(np_image, cls=True)

    lines: List[str] = []
    for page_result in results:
        for line in page_result:
            text = line[1][0]
            if text:
                lines.append(text)
    return "\n".join(lines)


def _is_pdf(filename: str, content_type: Optional[str]) -> bool:
    if content_type and "pdf" in content_type.lower():
        return True
    return filename.lower().endswith(".pdf")


def extract_text(file_bytes: bytes, filename: str, content_type: Optional[str] = None) -> str:
    """Detect file type, perform OCR, and return concatenated text."""

    if _is_pdf(filename, content_type):
        images = convert_from_bytes(file_bytes)
    else:
        image = Image.open(io.BytesIO(file_bytes))
        images = [image]

    page_texts: List[str] = []
    for image in images:
        page_texts.append(_extract_text_from_image(image))

    return "\n\n".join(filter(None, page_texts))
