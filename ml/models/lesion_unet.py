import torch
import torch.nn as nn
import torchvision.models as tvm


class LesionUNet(nn.Module):
    def __init__(self, num_classes: int = 4):
        super().__init__()
        encoder = tvm.efficientnet_b0(weights=tvm.EfficientNet_B0_Weights.IMAGENET1K_V1)
        self.features = encoder.features
        self.up1 = nn.ConvTranspose2d(1280, 320, 2, stride=2)
        self.up2 = nn.ConvTranspose2d(320, 128, 2, stride=2)
        self.up3 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.out = nn.Conv2d(64, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        f = self.features(x)
        x = self.up1(f)
        x = self.up2(x)
        x = self.up3(x)
        return torch.sigmoid(self.out(x))
