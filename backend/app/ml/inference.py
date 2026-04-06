from dataclasses import dataclass
from pathlib import Path

import cv2
import joblib
import numpy as np

from app.core.config import settings


@dataclass
class InferenceResult:
    dr_grade: int
    glaucoma: int
    cdr: float
    confidence: float
    risk_score: float
    uncertainty_mean: float
    uncertainty_std: float


class RetinalInferenceEngine:
    def __init__(self) -> None:
        self.dr_weights = np.array([0.05, 0.1, 0.2, 0.3, 0.35], dtype=np.float32)
        self.dr_model = None
        project_root = Path(__file__).resolve().parents[3]
        configured_dir = Path(settings.model_dir)
        search_dirs = [
            configured_dir,
            project_root / configured_dir,
            project_root / "ml/models/weights",
        ]

        model_candidates: list[Path] = []
        for d in search_dirs:
            model_candidates.extend([
                d / "diaretdb1_rf.joblib",
                d / "messidor2_rf.joblib",
            ])

        for model_path in model_candidates:
            if not model_path.exists():
                continue
            try:
                self.dr_model = joblib.load(model_path)
                break
            except Exception:
                self.dr_model = None

    @staticmethod
    def _extract_dr_features(visual_image: np.ndarray) -> np.ndarray:
        img = cv2.resize(visual_image, (512, 512), interpolation=cv2.INTER_AREA)
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 30, 120)
        edge_density = float(np.mean(edges > 0))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, kernel)
        vessel_density = float(np.mean(blackhat > 30))
        return np.array(
            [
                np.mean(r), np.mean(g), np.mean(b),
                np.std(r), np.std(g), np.std(b),
                np.mean(hsv[:, :, 0]), np.mean(hsv[:, :, 1]), np.mean(hsv[:, :, 2]),
                np.std(gray), np.mean(gray),
                edge_density, vessel_density,
                float(np.percentile(gray, 90)),
                float(np.percentile(gray, 10)),
            ],
            dtype=np.float32,
        )

    def _mc_dropout_uncertainty(self, features: np.ndarray, runs: int = 20) -> tuple[float, float]:
        preds = []
        for _ in range(runs):
            noise = np.random.normal(0, 0.015, size=features.shape)
            p = float(np.clip(np.mean(features + noise), 0.0, 1.0))
            preds.append(p)
        arr = np.array(preds)
        return float(np.mean(arr)), float(np.std(arr))

    def predict(
        self,
        processed_image: np.ndarray,
        estimated_cdr: float,
        visual_image: np.ndarray | None = None,
        vessel_map: np.ndarray | None = None,
    ) -> InferenceResult:
        features = np.clip((processed_image + 2.5) / 5.0, 0.0, 1.0)
        signal = float(np.mean(features[:, :, 1]))

        if visual_image is not None:
            red = visual_image[:, :, 0].astype(np.float32) / 255.0
            green = visual_image[:, :, 1].astype(np.float32) / 255.0
            red_bias = float(np.mean(np.clip(red - green, 0.0, 1.0)))
            texture = float(np.std(green))
        else:
            red_bias = 0.2
            texture = 0.2

        vessel_density = 0.25
        if vessel_map is not None and vessel_map.size > 0:
            vessel_density = float(np.mean(vessel_map > 35))

        texture_norm = float(np.clip(texture / 0.25, 0.0, 1.0))
        dr_index = float(np.clip(0.5 * red_bias + 0.3 * (1 - texture_norm) + 0.2 * (1 - vessel_density), 0.0, 1.0))

        if self.dr_model is not None and visual_image is not None:
            feats = self._extract_dr_features(visual_image).reshape(1, -1)
            try:
                dr_grade = int(np.clip(self.dr_model.predict(feats)[0], 0, 4))
            except Exception:
                dr_grade = 0
        else:
            if dr_index < 0.2:
                dr_grade = 0
            elif dr_index < 0.35:
                dr_grade = 1
            elif dr_index < 0.5:
                dr_grade = 2
            elif dr_index < 0.68:
                dr_grade = 3
            else:
                dr_grade = 4

        glaucoma_prob = float(np.clip(0.25 * signal + 0.55 * estimated_cdr + 0.2 * (1 - vessel_density), 0.0, 1.0))
        glaucoma = int(glaucoma_prob >= 0.5)
        confidence = float(np.clip(0.55 + 0.3 * abs(glaucoma_prob - 0.5) + 0.15 * texture_norm, 0.0, 0.99))

        combined = 0.55 * (dr_grade / 4.0) + 0.45 * glaucoma_prob
        risk_score = float(np.round(100 * combined, 2))

        unc_mean, unc_std = self._mc_dropout_uncertainty(features)

        return InferenceResult(
            dr_grade=dr_grade,
            glaucoma=glaucoma,
            cdr=float(np.round(estimated_cdr, 3)),
            confidence=float(np.round(confidence, 3)),
            risk_score=risk_score,
            uncertainty_mean=float(np.round(unc_mean, 4)),
            uncertainty_std=float(np.round(unc_std, 4)),
        )
