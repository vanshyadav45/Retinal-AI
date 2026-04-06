from __future__ import annotations

from pathlib import Path
import os

import numpy as np
import pandas as pd
import torch
import yaml
from sklearn.metrics import cohen_kappa_score, roc_auc_score
from torch import nn
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from torch.utils.data import DataLoader

from ml.datasets.dataset_loader import UnifiedRetinalDatasetBuilder
from ml.datasets.torch_dataset import RetinalTorchDataset
from ml.models.dr_classifier import DRClassifier
from ml.training.losses import qwk_proxy_loss, weighted_cross_entropy

try:
    import mlflow
except Exception:
    class _MLflowStub:
        @staticmethod
        def set_experiment(*args, **kwargs):
            return None

        class _Run:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

        @staticmethod
        def start_run(*args, **kwargs):
            return _MLflowStub._Run()

        @staticmethod
        def log_metric(*args, **kwargs):
            return None

    mlflow = _MLflowStub()


def train_dr(config_path: str = 'ml/configs/train.yaml') -> None:
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    mlflow.set_experiment('RetinalAI-DR')

    builder = UnifiedRetinalDatasetBuilder('data/raw')
    df = builder.build_master_csv(cfg['paths']['master_csv'])
    train_df, val_df = builder.patient_level_split(df)

    train_ds = RetinalTorchDataset(train_df, train=True)
    val_ds = RetinalTorchDataset(val_df, train=False)

    workers = 0 if os.name == 'nt' else cfg['num_workers']
    train_loader = DataLoader(train_ds, batch_size=cfg['batch_size'], shuffle=True, num_workers=workers)
    val_loader = DataLoader(val_ds, batch_size=cfg['batch_size'], shuffle=False, num_workers=workers)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = DRClassifier().to(device)

    class_counts = np.bincount(train_df['dr_grade'].astype(int), minlength=5) if len(train_df) else np.ones(5)
    class_weights = torch.tensor(1.0 / np.maximum(class_counts, 1), dtype=torch.float32, device=device)

    ce = weighted_cross_entropy(class_weights)
    opt = AdamW(model.parameters(), lr=cfg['learning_rate'])
    sched = CosineAnnealingWarmRestarts(opt, T_0=5)
    scaler = GradScaler(enabled=device == 'cuda')

    best_auc = -1.0
    best_path = Path(cfg['paths']['checkpoints']) / 'dr_best.pt'
    best_path.parent.mkdir(parents=True, exist_ok=True)

    patience = 0

    with mlflow.start_run():
        for epoch in range(cfg['epochs']):
            model.train()
            for batch in train_loader:
                x = batch['image'].to(device)
                y = batch['dr_grade'].to(device)

                opt.zero_grad(set_to_none=True)
                with autocast(enabled=device == 'cuda'):
                    logits = model(x)
                    loss = ce(logits, y) + 0.2 * qwk_proxy_loss(logits, y)

                scaler.scale(loss).backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg['grad_clip'])
                scaler.step(opt)
                scaler.update()

            sched.step(epoch + 1)

            model.eval()
            all_probs, all_targets = [], []
            with torch.no_grad():
                for batch in val_loader:
                    x = batch['image'].to(device)
                    y = batch['dr_grade'].to(device)
                    logits = model(x)
                    probs = torch.softmax(logits, dim=1)
                    all_probs.append(probs.cpu())
                    all_targets.append(y.cpu())

            if not all_probs:
                continue

            probs = torch.cat(all_probs).numpy()
            y_true = torch.cat(all_targets).numpy()
            y_pred = probs.argmax(axis=1)

            try:
                auc = roc_auc_score(pd.get_dummies(y_true), probs, multi_class='ovr')
            except Exception:
                auc = 0.0
            qwk = cohen_kappa_score(y_true, y_pred, weights='quadratic')

            mlflow.log_metric('val_auc', auc, step=epoch)
            mlflow.log_metric('val_qwk', qwk, step=epoch)

            if auc > best_auc:
                best_auc = auc
                torch.save({'model_state_dict': model.state_dict(), 'auc': auc, 'qwk': qwk}, best_path)
                patience = 0
            else:
                patience += 1

            if patience >= cfg['early_stopping_patience']:
                break


def main() -> None:
    train_dr()


if __name__ == '__main__':
    main()
