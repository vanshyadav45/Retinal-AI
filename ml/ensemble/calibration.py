import numpy as np


class TemperatureScaler:
    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature

    def fit(self, logits: np.ndarray, labels: np.ndarray) -> None:
        best_t, best_loss = 1.0, float('inf')
        for t in np.linspace(0.5, 5.0, 40):
            probs = 1 / (1 + np.exp(-logits / t))
            probs = np.clip(probs, 1e-6, 1 - 1e-6)
            loss = -np.mean(labels * np.log(probs) + (1 - labels) * np.log(1 - probs))
            if loss < best_loss:
                best_loss, best_t = loss, t
        self.temperature = float(best_t)

    def transform(self, logits: np.ndarray) -> np.ndarray:
        return logits / self.temperature


def weighted_ensemble(dr_score: float, glaucoma_score: float, w_dr: float = 0.55, w_glaucoma: float = 0.45) -> float:
    risk = 100 * (w_dr * dr_score + w_glaucoma * glaucoma_score)
    return float(np.clip(risk, 0.0, 100.0))
