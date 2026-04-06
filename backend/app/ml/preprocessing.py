import cv2
import numpy as np

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def extract_fundus_mask(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blur, 12, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        h, w = gray.shape
        fallback = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(fallback, (w // 2, h // 2), int(0.45 * min(h, w)), 255, -1)
        return fallback

    c = max(contours, key=cv2.contourArea)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [c], -1, 255, thickness=-1)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def circular_crop(image: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    if mask is not None:
        return cv2.bitwise_and(image, image, mask=mask)

    h, w, _ = image.shape
    center = (w // 2, h // 2)
    radius = min(center[0], center[1], int(0.48 * min(h, w)))
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    cropped = cv2.bitwise_and(image, image, mask=mask)
    return cropped


def ben_graham_preprocess(image: np.ndarray, sigma: int = 20) -> np.ndarray:
    blur = cv2.GaussianBlur(image, (0, 0), sigma)
    enhanced = cv2.addWeighted(image, 4.0, blur, -4.0, 128)
    return np.clip(enhanced, 0, 255).astype(np.uint8)


def clahe_green(image: np.ndarray) -> np.ndarray:
    green = image[:, :, 1]
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    green_eq = clahe.apply(green)
    merged = np.stack([green_eq, green_eq, green_eq], axis=-1)
    return merged


def gaussian_background_subtraction(image: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(image, (51, 51), 0)
    out = cv2.addWeighted(image, 1.5, blur, -0.5, 0)
    return np.clip(out, 0, 255).astype(np.uint8)


def resize_and_normalize(image: np.ndarray, size: int = 512) -> np.ndarray:
    image = cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)
    image = image.astype(np.float32) / 255.0
    image = (image - IMAGENET_MEAN) / IMAGENET_STD
    return image


def detect_optic_disc(image: np.ndarray) -> tuple[int, int, int]:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        h, w = gray.shape
        return w // 2, h // 2, min(h, w) // 8
    c = max(contours, key=cv2.contourArea)
    (x, y), r = cv2.minEnclosingCircle(c)
    return int(x), int(y), int(max(30, r))


def crop_optic_disc(image: np.ndarray, crop_size: int = 400) -> np.ndarray:
    cx, cy, _ = detect_optic_disc(image)
    half = crop_size // 2
    h, w, _ = image.shape
    x1, x2 = max(0, cx - half), min(w, cx + half)
    y1, y2 = max(0, cy - half), min(h, cy + half)
    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        crop = image
    return cv2.resize(crop, (crop_size, crop_size), interpolation=cv2.INTER_AREA)


def vessel_enhancement(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, kernel)
    vessel_map = cv2.normalize(blackhat, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return vessel_map


def estimate_cdr(optic_disc_crop: np.ndarray) -> float:
    gray = cv2.cvtColor(optic_disc_crop, cv2.COLOR_RGB2GRAY)
    _, disc = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    _, cup = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    disc_area = max(float(np.sum(disc > 0)), 1.0)
    cup_area = float(np.sum(cup > 0))
    cdr = np.sqrt(cup_area / disc_area)
    return float(np.clip(cdr, 0.1, 1.2))


def preprocess_full_pipeline(image: np.ndarray) -> dict:
    fundus_mask = extract_fundus_mask(image)
    step1 = circular_crop(image, fundus_mask)
    step2 = ben_graham_preprocess(step1)
    step3 = clahe_green(step2)
    step4 = gaussian_background_subtraction(step3)
    norm = resize_and_normalize(step4, size=512)
    optic_disc = crop_optic_disc(step4)
    vessel = vessel_enhancement(step4)
    cdr = estimate_cdr(optic_disc)
    return {
        "processed": norm,
        "visual": step4,
        "optic_disc": optic_disc,
        "vessel": vessel,
        "cdr": cdr,
        "fundus_mask": fundus_mask,
    }
