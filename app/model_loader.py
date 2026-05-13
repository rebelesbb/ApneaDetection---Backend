from fastapi import types
import torch
from torch.utils.data import Dataset
import numpy as np
import joblib
import sys
import types
import json
from pathlib import Path
from models_ml.tcn import TCNBinaryClassifier

class Scaler:
    def __init__(self, eps=1e-8):
        self.mean = None
        self.std = None
        self.eps = eps

    def fit(self, X):
        self.mean = np.nanmean(X, axis=(0,1)).astype(np.float32)
        self.std  = np.nanstd(X, axis=(0,1)).astype(np.float32)
        self.std = np.where(self.std < self.eps, 1.0, self.std)
        return self

    def transform(self, X):
        return (X - self.mean) / ((self.std if self.std is not None else 0) + self.eps)

    def fit_transform(self, X):
        return self.fit(X).transform(X)

class WindowDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.from_numpy(X).float()
        self.y = torch.from_numpy(y).float()

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

MODEL_REGISTRY = {
    "TCN": TCNBinaryClassifier,
}


def _register_scaler_for_joblib():
    main_module = sys.modules["__main__"]

    utils_module = types.ModuleType("utils")
    sys.modules["utils"] = utils_module

    model_module = types.ModuleType("utils.model_tcn")
    sys.modules["utils.model_tcn"] = model_module

    setattr(main_module, "Scaler", Scaler)
    setattr(model_module, "Scaler", Scaler)
    setattr(utils_module, "model_tcn", model_module)


def load_config(config_path="models/model_config.json"):
    config_path = Path(config_path)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config, config_path.parent


def load_trained_assets(config_path="models/model_config.json"):
    _register_scaler_for_joblib()

    config, config_dir = load_config(config_path)

    model_cfg = config["model"]

    model_type = model_cfg["type"]
    model_params = model_cfg.get("params", {})

    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model type: {model_type}")

    model_cls = MODEL_REGISTRY[model_type]
    model = model_cls(**model_params)

    checkpoint_path = Path(model_cfg["checkpoint_path"])
    scaler_path = Path(model_cfg["scaler_path"])

    if not checkpoint_path.is_absolute():
        checkpoint_path = config_dir.parent / checkpoint_path

    if not scaler_path.is_absolute():
        scaler_path = config_dir.parent / scaler_path

    device = "cuda" if torch.cuda.is_available() else "cpu"

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"],
        strict=True,
    )

    model = model.to(device)
    model.eval()

    scaler = joblib.load(scaler_path)

    return model, scaler, config