import base64
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def read_image_bytes(content: bytes) -> np.ndarray:
    np_arr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def image_to_base64(image: np.ndarray) -> str:
    pil_image = Image.fromarray(image)
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def blur_score(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def brightness_score(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return float(np.mean(gray))


def validate_retinal_fundus(image: np.ndarray) -> tuple[bool, str]:
    h, w, _ = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    non_black = (gray > 12).astype(np.uint8)
    non_black_ratio = float(np.mean(non_black))
    if non_black_ratio < 0.2:
        return False, "Image is too dark or empty. Please upload a clear retinal fundus photo."

    contours, _ = cv2.findContours((non_black * 255).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False, "No retinal region found. Only retinal fundus images are accepted."

    largest = max(contours, key=cv2.contourArea)
    area = float(cv2.contourArea(largest))
    perimeter = float(cv2.arcLength(largest, True)) + 1e-8
    circularity = float(4 * np.pi * area / (perimeter * perimeter))
    area_ratio = area / float(h * w)

    if area_ratio < 0.18 or circularity < 0.35:
        return False, "This does not look like a retinal fundus image. Please upload an eye fundus scan only."

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    retinal_tone_ratio = float(np.mean(((hue <= 35) | (hue >= 160)) & (sat > 25)))
    if retinal_tone_ratio < 0.2:
        return False, "Unsupported image content. Please upload a retinal fundus image."

    center_patch = gray[h // 3 : 2 * h // 3, w // 3 : 2 * w // 3]
    if center_patch.size == 0 or float(np.std(center_patch)) < 8.0:
        return False, "Retinal detail is insufficient. Please upload a higher-quality fundus photo."

    edges = cv2.Canny(gray, 30, 120)
    edge_density = float(np.mean(edges > 0))
    if edge_density < 0.0002 or edge_density > 0.4:
        return False, "Only retinal eye fundus images are accepted. Please upload a retinal scan."

    return True, "ok"
