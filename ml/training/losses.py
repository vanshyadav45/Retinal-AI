import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        p_t = torch.exp(-bce)
        focal = self.alpha * (1 - p_t) ** self.gamma * bce
        return focal.mean()


def weighted_cross_entropy(class_weights: torch.Tensor):
    return nn.CrossEntropyLoss(weight=class_weights)


def qwk_proxy_loss(logits: torch.Tensor, targets: torch.Tensor, n_classes: int = 5) -> torch.Tensor:
    probs = torch.softmax(logits, dim=1)
    onehot = F.one_hot(targets, num_classes=n_classes).float()
    diff = torch.abs(probs - onehot)
    penalty = diff * torch.arange(1, n_classes + 1, device=logits.device).float()
    return penalty.mean()
