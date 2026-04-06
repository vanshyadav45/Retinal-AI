from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold


def build_group_folds(df: pd.DataFrame, n_splits: int = 5):
    gkf = GroupKFold(n_splits=n_splits)
    for fold, (train_idx, val_idx) in enumerate(gkf.split(df, groups=df['patient_id'])):
        yield fold, df.iloc[train_idx].reset_index(drop=True), df.iloc[val_idx].reset_index(drop=True)


def paired_bootstrap_test(scores_a: np.ndarray, scores_b: np.ndarray, n_bootstrap: int = 1000) -> float:
    diffs = []
    n = len(scores_a)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        diffs.append(np.mean(scores_a[idx] - scores_b[idx]))
    diffs = np.array(diffs)
    p_value = 2 * min(np.mean(diffs >= 0), np.mean(diffs <= 0))
    return float(p_value)
