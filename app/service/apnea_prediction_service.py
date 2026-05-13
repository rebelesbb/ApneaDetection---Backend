from typing import List, Optional, Tuple

import numpy as np
import torch
from scipy.signal import find_peaks

from app.model_loader import load_trained_assets


class ApneaPredictionService:
    def __init__(self, config_path: str = "models_ml/model_config.json"):
        self.model, self.scaler, self.config = load_trained_assets(config_path)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model.to(self.device)
        self.model.eval()

        pp = self.config["postprocessing"]

        self.window_size = int(pp["window_size"])
        self.step = int(pp["step"])

        self.threshold = float(pp["threshold"])
        self.min_distance_sec = int(pp["min_distance_sec"])
        self.smoothing_window = int(pp["smoothing_window"])

        self.max_interp_gap_sec = int(pp.get("max_interp_gap_sec", 5))

        self.spo2_min = float(pp.get("spo2_min", 60.0))
        self.spo2_max = float(pp.get("spo2_max", 100.0))

    def _clean_spo2(self, values: np.ndarray) -> np.ndarray:
        values = values.astype(np.float32).copy()
        values[(values < self.spo2_min) | (values > self.spo2_max)] = np.nan
        return values

    def _interpolate_short_nan_gaps(self, values: np.ndarray) -> np.ndarray:
        values = values.astype(np.float32).copy()
        n = len(values)

        i = 0
        while i < n:
            if not np.isnan(values[i]):
                i += 1
                continue

            start = i

            while i < n and np.isnan(values[i]):
                i += 1

            end = i
            gap_len = end - start

            left = start - 1
            right = end

            can_interpolate = (
                gap_len <= self.max_interp_gap_sec
                and left >= 0
                and right < n
                and not np.isnan(values[left])
                and not np.isnan(values[right])
            )

            if can_interpolate:
                values[start:end] = np.linspace(
                    values[left],
                    values[right],
                    gap_len + 2,
                    dtype=np.float32
                )[1:-1]

        return values

    def _smooth_probs(self, probs: np.ndarray) -> np.ndarray:
        if self.smoothing_window <= 1:
            return probs.copy()

        kernel = np.ones(self.smoothing_window, dtype=np.float32) / self.smoothing_window
        return np.convolve(probs, kernel, mode="same")

    def _make_sleep_mask(
        self,
        n: int,
        stages: Optional[List[int]] = None,
    ) -> np.ndarray:
        if stages is None:
            return np.ones(n, dtype=np.int8)

        stages_arr = np.asarray(stages)

        if len(stages_arr) != n:
            raise ValueError("Stages and SpO2 values must have the same length.")

        sleep_mask = (stages_arr != 0).astype(np.int8)

        return sleep_mask

    def _make_windows(self, spo2_values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        n = len(spo2_values)

        windows = []
        centers = []

        for start in range(0, n - self.window_size + 1, self.step):
            end = start + self.window_size
            window = spo2_values[start:end]

            if np.isnan(window).any():
                continue

            windows.append(window)
            centers.append(start + self.window_size // 2)

        if len(windows) == 0:
            return (
                np.empty((0, self.window_size, 1), dtype=np.float32),
                np.empty((0,), dtype=np.int64),
            )

        x = np.asarray(windows, dtype=np.float32)[..., None]
        centers = np.asarray(centers, dtype=np.int64)

        return x, centers

    def _predict_onset_probs(self, x: np.ndarray) -> np.ndarray:
        x_scaled = self.scaler.transform(x)

        x_tensor = torch.tensor(x_scaled, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            logits = self.model(x_tensor).view(-1)
            probs = torch.sigmoid(logits).cpu().numpy()

        return probs.astype(np.float32)

    def predict(
        self,
        values: List[float],
        timestamps: List[int],
        stages: Optional[List[int]] = None,
    ) -> Tuple[float, List[int]]:
        if len(values) != len(timestamps):
            raise ValueError("Values and timestamps must have the same length.")

        if len(values) < self.window_size:
            raise ValueError(
                f"Insufficient data for prediction. "
                f"At least {self.window_size} values are required."
            )

        spo2_values = np.asarray(values, dtype=np.float32)
        spo2_values = self._clean_spo2(spo2_values)
        spo2_values = self._interpolate_short_nan_gaps(spo2_values)

        sleep_mask = self._make_sleep_mask(
            n=len(spo2_values),
            stages=stages,
        )

        x, centers = self._make_windows(spo2_values)

        if len(x) == 0:
            raise ValueError("No valid windows available after SpO2 cleaning.")

        win_probs = self._predict_onset_probs(x)

        onset_probs = np.zeros(len(spo2_values), dtype=np.float32)
        onset_probs[centers] = win_probs

        onset_probs[sleep_mask == 0] = 0.0

        probs_smooth = self._smooth_probs(onset_probs)

        probs_smooth[sleep_mask == 0] = 0.0

        pred_onsets, _ = find_peaks(
            probs_smooth,
            height=self.threshold,
            distance=self.min_distance_sec,
        )

        pred_onsets = pred_onsets[sleep_mask[pred_onsets] == 1]

        sleep_hours = sleep_mask.sum() / 3600.0

        if sleep_hours <= 0:
            ahi_pred = 0.0
        else:
            ahi_pred = len(pred_onsets) / sleep_hours

        pred_binary = np.zeros(len(spo2_values), dtype=np.int8)
        pred_binary[pred_onsets] = 1

        return float(ahi_pred), pred_binary.tolist()