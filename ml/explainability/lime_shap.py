from __future__ import annotations

import numpy as np


class LimeExplainerStub:
    def explain(self, image: np.ndarray) -> np.ndarray:
        h, w, _ = image.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] = 255
        return mask


class DeepShapStub:
    def explain(self, image: np.ndarray) -> np.ndarray:
        importance = np.mean(image.astype(np.float32), axis=2)
        importance = (importance - importance.min()) / (importance.max() - importance.min() + 1e-8)
        return importance
