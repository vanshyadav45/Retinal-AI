import numpy as np
import torch


def mixup(images: torch.Tensor, labels: torch.Tensor, alpha: float = 0.4):
    if alpha <= 0:
        return images, labels, labels, 1.0
    lam = np.random.beta(alpha, alpha)
    idx = torch.randperm(images.size(0), device=images.device)
    mixed = lam * images + (1 - lam) * images[idx]
    return mixed, labels, labels[idx], lam


def cutmix(images: torch.Tensor, labels: torch.Tensor, alpha: float = 1.0):
    lam = np.random.beta(alpha, alpha)
    idx = torch.randperm(images.size(0), device=images.device)
    bbx1, bby1, bbx2, bby2 = rand_bbox(images.size(), lam)
    images[:, :, bby1:bby2, bbx1:bbx2] = images[idx, :, bby1:bby2, bbx1:bbx2]
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (images.size(-1) * images.size(-2)))
    return images, labels, labels[idx], lam


def rand_bbox(size, lam):
    w = size[3]
    h = size[2]
    cut_rat = np.sqrt(1.0 - lam)
    cut_w = int(w * cut_rat)
    cut_h = int(h * cut_rat)

    cx = np.random.randint(w)
    cy = np.random.randint(h)

    bbx1 = np.clip(cx - cut_w // 2, 0, w)
    bby1 = np.clip(cy - cut_h // 2, 0, h)
    bbx2 = np.clip(cx + cut_w // 2, 0, w)
    bby2 = np.clip(cy + cut_h // 2, 0, h)
    return bbx1, bby1, bbx2, bby2
