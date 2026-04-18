import cv2
import pytesseract
import re
import os

TEMP_DIR = "scanner/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def clean_ocr_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^A-Za-z'\- ]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text if len(text) >= 4 else ""

def scan_card_name(image_path: str) -> str:
    card_image = cv2.imread(image_path)
    h, w, _ = card_image.shape

    # Crop name bar (these values are fine)
    top = int(h * 0.04)
    bottom = int(h * 0.11)
    left = int(w * 0.07)
    right = int(w * 0.92)

    name_crop = card_image[top:bottom, left:right]

    # Upscale
    enlarged = cv2.resize(
        name_crop, None,
        fx=2, fy=2,
        interpolation=cv2.INTER_CUBIC
    )
    cv2.imwrite(f"{TEMP_DIR}/enlarged.jpg", enlarged)

    config = (
        "--psm 6 "
        "-c tessedit_char_whitelist="
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-' "
    )

    raw_text = pytesseract.image_to_string(enlarged, config=config)

    return clean_ocr_text(raw_text)

def retry_with_gray_filter() -> str:
    enlarged = cv2.imread(f"{TEMP_DIR}/enlarged.jpg")
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"{TEMP_DIR}/gray.jpg", gray)

    config = (
        "--psm 6 "
        "-c tessedit_char_whitelist="
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-' "
    )

    raw_text = pytesseract.image_to_string(gray, config=config)
    return clean_ocr_text(raw_text)

def retry_with_adaptive_threshold() -> str:
    gray = cv2.imread(f"{TEMP_DIR}/gray.jpg")
    
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f"{TEMP_DIR}/thresh.jpg", thresh)

    config = (
        "--psm 6 "
        "-c tessedit_char_whitelist="
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-' "
    )

    raw_text = pytesseract.image_to_string(thresh, config=config)
    return clean_ocr_text(raw_text)
