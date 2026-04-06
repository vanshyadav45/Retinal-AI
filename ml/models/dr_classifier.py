import torch
import torch.nn as nn
import torchvision.models as tvm


class DRClassifier(nn.Module):
    def __init__(self, num_classes: int = 5):
        super().__init__()
        backbone = tvm.efficientnet_b4(weights=tvm.EfficientNet_B4_Weights.IMAGENET1K_V1)
        in_features = backbone.classifier[1].in_features
        backbone.classifier[1] = nn.Linear(in_features, num_classes)
        self.model = backbone

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)
