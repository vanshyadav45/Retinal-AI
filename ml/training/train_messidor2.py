from __future__ import annotations

from pathlib import Path

import cv2
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import cohen_kappa_score, f1_score
from sklearn.model_selection import GroupShuffleSplit

from ml.datasets.dataset_loader import UnifiedRetinalDatasetBuilder


def extract_features(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        return np.zeros(15, dtype=np.float32)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)

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

    feats = np.array(
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
    return feats


def main() -> None:
    builder = UnifiedRetinalDatasetBuilder("data/raw")
    df = builder.build_master_csv("data/metadata/master_dataset.csv")
    messidor = df[df["dataset"] == "MESSIDOR2"].copy()

    if messidor.empty:
        raise RuntimeError(
            "No MESSIDOR2 samples found. Place images under data/raw/MESSIDOR2 and labels in labels.csv/labels.xlsx."
        )

    X = np.stack([extract_features(p) for p in messidor["image_path"].tolist()])
    y = messidor["dr_grade"].astype(int).values
    groups = messidor["patient_id"].astype(str).values

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, val_idx = next(splitter.split(X, y, groups=groups))

    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_val)
    qwk = cohen_kappa_score(y_val, pred, weights="quadratic")
    f1 = f1_score(y_val, pred, average="macro")

    out_dir = Path("ml/models/weights")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "messidor2_rf.joblib"
    joblib.dump(model, out_path)

    metrics = {
        "samples": int(len(messidor)),
        "train": int(len(train_idx)),
        "val": int(len(val_idx)),
        "qwk": float(qwk),
        "f1_macro": float(f1),
        "model_path": str(out_path),
    }
    pd.DataFrame([metrics]).to_csv("reports/generated/messidor2_training_metrics.csv", index=False)

    print(f"Training complete. QWK={qwk:.4f}, F1={f1:.4f}")
    print(f"Saved model: {out_path}")


if __name__ == "__main__":
    main()
