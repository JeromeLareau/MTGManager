import cv2
import numpy as np

from constant import TEMP_DIR

def detect_card(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 75, 200)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    
    image_area = image.shape[0] * image.shape[1]
    candidates = []

    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < image_area * 0.15:
            continue  # too small to be a card

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        if len(approx) != 4:
            continue

        x, y, w, h = cv2.boundingRect(approx)
        ratio = max(w, h) / min(w, h)

        if 1.2 < ratio < 1.6:
            candidates.append((area, approx))

    if not candidates:
            return None
    
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def warp_card(image, contour):
    pts = contour.reshape(4, 2)

    def order_points(pts):
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        return np.array([
            pts[np.argmin(s)],
            pts[np.argmin(diff)],
            pts[np.argmax(s)],
            pts[np.argmax(diff)]
        ], dtype="float32")

    rect = order_points(pts)

    width = int(max(
        np.linalg.norm(rect[0] - rect[1]),
        np.linalg.norm(rect[2] - rect[3])
    ))

    height = int(max(
        np.linalg.norm(rect[0] - rect[3]),
        np.linalg.norm(rect[1] - rect[2])
    ))

    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (width, height))
