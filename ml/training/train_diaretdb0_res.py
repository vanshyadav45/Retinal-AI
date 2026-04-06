from __future__ import annotations

import json
from pathlib import Path

import cv2
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit


RES_DIR = Path("data/raw/DIARETDB1/diaretdb0_v_1_1/resources/example_evalresults")
IMG_DIR = Path("data/raw/DIARETDB1/diaretdb0_v_1_1/resources/images/diaretdb0_binary_masks")


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
            np.mean(r),
            np.mean(g),
            np.mean(b),
            np.std(r),
            np.std(g),
            np.std(b),
            np.mean(hsv[:, :, 0]),
            np.mean(hsv[:, :, 1]),
            np.mean(hsv[:, :, 2]),
            np.std(gray),
            np.mean(gray),
            edge_density,
            vessel_density,
            float(np.percentile(gray, 90)),
            float(np.percentile(gray, 10)),
        ],
        dtype=np.float32,
    )
    return feats


def dr_grade_from_tokens(tokens: list[str]) -> int:
    values = [t.strip().lower() for t in tokens]
    while len(values) < 5:
        values.append("n/a")

    redsmall = values[0] != "n/a"
    hemorrhage = values[1] != "n/a"
    hard_exudate = values[2] != "n/a"
    soft_exudate = values[3] != "n/a"
    neovascular = values[4] != "n/a"

    if neovascular:
        return 4

    lesion_count = int(redsmall) + int(hemorrhage) + int(hard_exudate) + int(soft_exudate)
    if lesion_count == 0:
        return 0
    if lesion_count == 1 and redsmall and not (hemorrhage or hard_exudate or soft_exudate):
        return 1
    if lesion_count <= 2:
        return 2
    return 3


def build_dataset_from_res() -> pd.DataFrame:
    if not RES_DIR.exists():
        raise RuntimeError(f"Results directory not found: {RES_DIR}")
    if not IMG_DIR.exists():
        raise RuntimeError(f"Image directory not found: {IMG_DIR}")

    rows: list[dict] = []
    for res_file in sorted(RES_DIR.glob("*.res")):
        stem = res_file.stem
        image_name = f"{stem}_valid.png"
        image_path = IMG_DIR / image_name
        if not image_path.exists():
            continue

        line = res_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not line:
            continue

        tokens = line.split()
        rows.append(
            {
                "dataset": "DIARETDB1",
                "patient_id": f"DIARETDB1_{stem}",
                "image_path": str(image_path),
                "dr_grade": dr_grade_from_tokens(tokens),
                "glaucoma": 0,
                "cdr": 0.45,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No DIARETDB samples paired from .res and *_valid.png files")
    return df


def main() -> None:
    df = build_dataset_from_res()

    meta_out = Path("data/metadata/diaretdb1_only.csv")
    meta_out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(meta_out, index=False)

    X = np.stack([extract_features(p) for p in df["image_path"].tolist()])
    y = df["dr_grade"].astype(int).values
    groups = df["patient_id"].astype(str).values

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, val_idx = next(splitter.split(X, y, groups=groups))

    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=14,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_val)

    out_dir = Path("ml/models/weights")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "diaretdb1_rf.joblib"
    joblib.dump(model, out_path)

    metrics = {
        "dataset": "DIARETDB1_from_res",
        "samples": int(len(df)),
        "train": int(len(train_idx)),
        "val": int(len(val_idx)),
        "accuracy": float(accuracy_score(y_val, pred)),
        "qwk": float(cohen_kappa_score(y_val, pred, weights="quadratic")),
        "f1_macro": float(f1_score(y_val, pred, average="macro", zero_division=0)),
        "precision_macro": float(precision_score(y_val, pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_val, pred, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_val, pred, labels=[0, 1, 2, 3, 4]).tolist(),
        "classification_report": classification_report(y_val, pred, labels=[0, 1, 2, 3, 4], output_dict=True, zero_division=0),
        "model_path": str(out_path),
    }

    report_dir = Path("reports/generated")
    report_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{k: v for k, v in metrics.items() if not isinstance(v, (list, dict))}]).to_csv(
        report_dir / "diaretdb1_training_metrics.csv", index=False
    )
    (report_dir / "diaretdb1_training_scores.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Training complete for DIARETDB-only model.")
    print(f"Accuracy={metrics['accuracy']:.4f}, QWK={metrics['qwk']:.4f}, F1={metrics['f1_macro']:.4f}")
    print(f"Saved model: {out_path}")
    print(f"Saved metrics: {report_dir / 'diaretdb1_training_metrics.csv'}")
    print(f"Saved detailed scores: {report_dir / 'diaretdb1_training_scores.json'}")


if __name__ == "__main__":
    main()
