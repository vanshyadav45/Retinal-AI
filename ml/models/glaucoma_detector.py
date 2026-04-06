import torch
import torch.nn as nn
import torchvision.models as tvm


class GlaucomaDetector(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = tvm.resnet50(weights=tvm.ResNet50_Weights.IMAGENET1K_V2)
        in_features = backbone.fc.in_features
        backbone.fc = nn.Identity()
        self.backbone = backbone
        self.head = nn.Sequential(
            nn.Linear(in_features * 2, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 2),
        )

    def forward(self, full_img: torch.Tensor, disc_crop: torch.Tensor):
        f1 = self.backbone(full_img)
        f2 = self.backbone(disc_crop)
        fused = torch.cat([f1, f2], dim=1)
        out = self.head(fused)
        glaucoma_logit = out[:, 0]
        cdr_reg = torch.sigmoid(out[:, 1]) * 1.2
        return glaucoma_logit, cdr_reg
