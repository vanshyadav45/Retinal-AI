from __future__ import annotations

import cv2
import numpy as np


def gradcam_overlay(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    heat = cv2.GaussianBlur(gray, (0, 0), sigmaX=18)
    heat = cv2.normalize(heat, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(image, 0.65, color, 0.35, 0)


def eigencam_overlay(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)
    mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    color = cv2.applyColorMap(mag, cv2.COLORMAP_TURBO)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(image, 0.65, color, 0.35, 0)
