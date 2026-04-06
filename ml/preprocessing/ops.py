from __future__ import annotations

import cv2
import numpy as np


def clahe_enhancement(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    merged = cv2.merge([l2, a, b])
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)


def green_channel_extract(image: np.ndarray) -> np.ndarray:
    g = image[:, :, 1]
    return np.stack([g, g, g], axis=-1)


def ben_graham(image: np.ndarray, sigma: int = 10) -> np.ndarray:
    blur = cv2.GaussianBlur(image, (0, 0), sigma)
    return cv2.addWeighted(image, 4, blur, -4, 128)


def circular_crop(image: np.ndarray) -> np.ndarray:
    h, w, _ = image.shape
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (w // 2, h // 2), int(min(h, w) * 0.48), 255, -1)
    return cv2.bitwise_and(image, image, mask=mask)


def gaussian_bg_subtraction(image: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(image, (51, 51), 0)
    return cv2.addWeighted(image, 1.5, blur, -0.5, 0)


def vessel_enhance_frangi(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, kernel)
    return cv2.normalize(blackhat, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def optic_disc_detect(image: np.ndarray) -> tuple[int, int, int]:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, t = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        h, w = gray.shape
        return w // 2, h // 2, 60
    c = max(cnts, key=cv2.contourArea)
    (x, y), r = cv2.minEnclosingCircle(c)
    return int(x), int(y), int(r)


def optic_disc_crop(image: np.ndarray, size: int = 400) -> np.ndarray:
    x, y, _ = optic_disc_detect(image)
    h, w, _ = image.shape
    half = size // 2
    x1, x2 = max(0, x - half), min(w, x + half)
    y1, y2 = max(0, y - half), min(h, y + half)
    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        crop = image
    return cv2.resize(crop, (size, size))


def cdr_calculate(cup_mask: np.ndarray, disc_mask: np.ndarray) -> float:
    disc_area = max(np.sum(disc_mask > 0), 1)
    cup_area = np.sum(cup_mask > 0)
    return float(np.sqrt(cup_area / disc_area))
