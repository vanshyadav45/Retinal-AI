from __future__ import annotations

import cv2
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from ml.preprocessing.transforms import train_transforms, val_transforms


class RetinalTorchDataset(Dataset):
    def __init__(self, df: pd.DataFrame, train: bool = True):
        self.df = df.reset_index(drop=True)
        self.transforms = train_transforms() if train else val_transforms()

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        image = cv2.imread(row.image_path)
        if image is None:
            image = np.zeros((512, 512, 3), dtype=np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        transformed = self.transforms(image=image)
        tensor = transformed["image"]

        return {
            "image": tensor,
            "dr_grade": torch.tensor(int(row.dr_grade), dtype=torch.long),
            "glaucoma": torch.tensor(float(row.glaucoma), dtype=torch.float32),
            "cdr": torch.tensor(float(row.cdr), dtype=torch.float32),
        }
