import cv2
import numpy as np


def gradcam_like_overlay(image: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    heat = cv2.GaussianBlur(gray, (0, 0), sigmaX=21)
    heat = cv2.normalize(heat, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    heat = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(image, 0.55, heat, 0.45, 0)
    if mask is not None:
        masked_overlay = cv2.bitwise_and(overlay, overlay, mask=mask)
        # Non-retinal regions are explicitly darkened to avoid scanning/highlighting outside the eye.
        background = np.zeros_like(image)
        overlay = np.where(mask[..., None] > 0, masked_overlay, background)
    return overlay


def fake_lesion_mask(image: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    h, w, _ = image.shape
    lesion = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.circle(lesion, (w // 3, h // 3), 22, (255, 0, 0), -1)
    cv2.circle(lesion, (w // 2, h // 2), 18, (255, 255, 0), -1)
    cv2.circle(lesion, (2 * w // 3, h // 2), 12, (0, 0, 255), -1)
    cv2.circle(lesion, (w // 2, 2 * h // 3), 15, (0, 255, 0), -1)
    if mask is not None:
        lesion = np.where(mask[..., None] > 0, lesion, 0)
        base = cv2.bitwise_and(image, image, mask=mask)
    else:
        base = image
    return cv2.addWeighted(base, 0.75, lesion, 0.25, 0)
