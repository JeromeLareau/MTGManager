import cv2
import pytesseract
import re

from constant import TEMP_DIR

OCR_CONFIG = (
        "--psm 6 "
        "-c tessedit_char_whitelist="
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-' "
    )

def clean_ocr_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^A-Za-z'\- ]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text if len(text) >= 4 else ""

def scan_card_name(image) -> str:
    h, w, _ = image.shape

    # Crop name bar (these values are fine)
    top = int(h * 0)
    bottom = int(h * 0.10)
    left = int(w * 0.05)
    right = int(w * 0.90)

    name_crop = image[top:bottom, left:right]

    # Upscale
    enlarged = cv2.resize(
        name_crop, None,
        fx=2, fy=2,
        interpolation=cv2.INTER_CUBIC
    )
    cv2.imwrite(f"{TEMP_DIR}/enlarged.jpg", enlarged)

    raw_text = pytesseract.image_to_string(enlarged, config=OCR_CONFIG)

    return clean_ocr_text(raw_text)

def retry_with_gray_filter() -> str:
    enlarged = cv2.imread(f"{TEMP_DIR}/enlarged.jpg")
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"{TEMP_DIR}/gray.jpg", gray)

    raw_text = pytesseract.image_to_string(gray, config=OCR_CONFIG)
    return clean_ocr_text(raw_text)

def retry_with_adaptive_threshold() -> str:
    gray = cv2.imread(f"{TEMP_DIR}/gray.jpg")
    
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f"{TEMP_DIR}/thresh.jpg", thresh)

    raw_text = pytesseract.image_to_string(thresh, config=OCR_CONFIG)
    return clean_ocr_text(raw_text)
