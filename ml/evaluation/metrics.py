import numpy as np
from sklearn.metrics import (
    auc,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


def sensitivity_specificity(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sens = tp / (tp + fn + 1e-8)
    spec = tn / (tn + fp + 1e-8)
    return float(sens), float(spec)


def compute_binary_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    y_pred = (y_prob >= 0.5).astype(int)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    sens, spec = sensitivity_specificity(y_true, y_pred)

    return {
        'auc_roc': float(roc_auc_score(y_true, y_prob)),
        'f1': float(f1_score(y_true, y_pred)),
        'sensitivity': sens,
        'specificity': spec,
        'roc_curve': list(zip(fpr.tolist(), tpr.tolist())),
        'pr_curve': list(zip(rec.tolist(), prec.tolist())),
        'pr_auc': float(auc(rec, prec)),
    }


def dice_score(pred_mask: np.ndarray, true_mask: np.ndarray) -> float:
    pred = (pred_mask > 0.5).astype(np.float32)
    true = (true_mask > 0.5).astype(np.float32)
    inter = (pred * true).sum()
    denom = pred.sum() + true.sum() + 1e-8
    return float((2 * inter) / denom)
