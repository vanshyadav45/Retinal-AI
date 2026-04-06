from __future__ import annotations

from pathlib import Path
import os

import numpy as np
import torch
import yaml
from sklearn.metrics import roc_auc_score
from torch import nn
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from torch.utils.data import DataLoader

from ml.datasets.dataset_loader import UnifiedRetinalDatasetBuilder
from ml.datasets.torch_dataset import RetinalTorchDataset
from ml.models.glaucoma_detector import GlaucomaDetector
from ml.training.losses import FocalLoss

try:
    import mlflow
except Exception:
    class _MLflowStub:
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


def train_glaucoma(config_path: str = 'ml/configs/train.yaml') -> None:
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    builder = UnifiedRetinalDatasetBuilder('data/raw')
    df = builder.build_master_csv(cfg['paths']['master_csv'])
    train_df, val_df = builder.patient_level_split(df)

    workers = 0 if os.name == 'nt' else cfg['num_workers']
    train_loader = DataLoader(
        RetinalTorchDataset(train_df, train=True),
        batch_size=cfg['batch_size'],
        shuffle=True,
        num_workers=workers,
    )
    val_loader = DataLoader(
        RetinalTorchDataset(val_df, train=False),
        batch_size=cfg['batch_size'],
        shuffle=False,
        num_workers=workers,
    )

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = GlaucomaDetector().to(device)

    focal = FocalLoss()
    mse = nn.MSELoss()
    opt = AdamW(model.parameters(), lr=cfg['learning_rate'])
    sched = CosineAnnealingWarmRestarts(opt, T_0=5)
    scaler = GradScaler(enabled=device == 'cuda')

    best_auc = -1.0
    best_path = Path(cfg['paths']['checkpoints']) / 'glaucoma_best.pt'
    best_path.parent.mkdir(parents=True, exist_ok=True)

    with mlflow.start_run(run_name='glaucoma_training'):
        for epoch in range(cfg['epochs']):
            model.train()
            for batch in train_loader:
                x = batch['image'].to(device)
                g = batch['glaucoma'].to(device)
                cdr = batch['cdr'].to(device)

                opt.zero_grad(set_to_none=True)
                with autocast(enabled=device == 'cuda'):
                    logit, cdr_hat = model(x, x)
                    loss = focal(logit, g) + 0.4 * mse(cdr_hat, cdr)

                scaler.scale(loss).backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg['grad_clip'])
                scaler.step(opt)
                scaler.update()

            sched.step(epoch + 1)

            model.eval()
            y_true, y_prob = [], []
            with torch.no_grad():
                for batch in val_loader:
                    x = batch['image'].to(device)
                    g = batch['glaucoma'].to(device)
                    logit, _ = model(x, x)
                    prob = torch.sigmoid(logit)
                    y_true.extend(g.cpu().numpy().tolist())
                    y_prob.extend(prob.cpu().numpy().tolist())

            if y_true:
                auc = roc_auc_score(y_true, y_prob)
                mlflow.log_metric('val_auc', auc, step=epoch)
                if auc > best_auc:
                    best_auc = auc
                    torch.save({'model_state_dict': model.state_dict(), 'auc': auc}, best_path)


def main() -> None:
    train_glaucoma()


if __name__ == '__main__':
    main()
