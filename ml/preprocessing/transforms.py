try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
except Exception:
    A = None
    ToTensorV2 = None

import cv2
import numpy as np
import torch


def train_transforms(image_size: int = 512):
    if A is None or ToTensorV2 is None:
        def _fallback(image):
            img = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
            img = img.astype(np.float32) / 255.0
            img = (img - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
            tensor = torch.from_numpy(np.transpose(img, (2, 0, 1))).float()
            return {"image": tensor}

        class _Wrapper:
            def __call__(self, image):
                return _fallback(image)

        return _Wrapper()

    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.2),
            A.Rotate(limit=30, p=0.6),
            A.ColorJitter(p=0.5),
            A.ElasticTransform(alpha=1.0, sigma=50, p=0.25),
            A.GridDistortion(p=0.25),
            A.OpticalDistortion(p=0.25),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ]
    )


def val_transforms(image_size: int = 512):
    if A is None or ToTensorV2 is None:
        def _fallback(image):
            img = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
            img = img.astype(np.float32) / 255.0
            img = (img - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
            tensor = torch.from_numpy(np.transpose(img, (2, 0, 1))).float()
            return {"image": tensor}

        class _Wrapper:
            def __call__(self, image):
                return _fallback(image)

        return _Wrapper()

    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ]
    )
