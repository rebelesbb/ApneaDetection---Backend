from typing import List, Tuple

import numpy as np
import torch

from app.model_loader import load_trained_assets

class ApneaPredictionService:
    def __init__(self):
        self.model, self.scaler = load_trained_assets()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model.to(self.device)
        self.model.eval()

        self.window_size = 60
        self.threshold = 0.475

    def predict(self, values: List[float], timestamps: List[int]) -> Tuple[float, List[int]]:
        if len(values) != len(timestamps):
            raise ValueError("Values and timestamps must have the same length.")

        if len(values) < self.window_size:
            raise ValueError("Insufficient data for prediction. At least 60 values are required.")

        spo2_values = np.array(values, dtype=np.float32)

        num_windows = len(spo2_values) // self.window_size
        if num_windows == 0:
            raise ValueError("Insufficient data for prediction. At least 60 values are required.")

        trimmed_values = spo2_values[:num_windows * self.window_size]

        x = trimmed_values.reshape(num_windows, self.window_size, 1)

        x_flattened = x.reshape(-1, 1)
        x_scaled = self.scaler.transform(x_flattened).reshape(num_windows, self.window_size, 1)

        x_tensor = torch.tensor(x_scaled, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            logits = self.model(x_tensor)
            probs = torch.sigmoid(logits).cpu().numpy().flatten()

        win_pred = (probs >= self.threshold).astype(int)

        n_events = np.sum(np.diff(win_pred) > 0)
        total_hours = len(trimmed_values) / 3600
        ahi_pred = n_events / total_hours if total_hours > 0 else 0.0

        return float(ahi_pred), win_pred.tolist()