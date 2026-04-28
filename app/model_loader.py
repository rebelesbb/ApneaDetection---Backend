from fastapi import types
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
import numpy as np
import joblib
import sys
import types

class TemporalBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int, dilation: int, droptout: float):
        super().__init__()
        padding = ((kernel_size - 1) * dilation) // 2

        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding, dilation=dilation)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size, padding=padding, dilation=dilation)

        self.dropout = nn.Dropout(droptout)
        self.relu = nn.ReLU()

        self.downsample = None
        if in_channels != out_channels:
            self.downsample = nn.Conv1d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        out = self.conv1(x)
        out = self.relu(out)
        out = self.dropout(out)

        out = self.conv2(out)
        out = self.relu(out)
        out = self.dropout(out)

        res = x if self.downsample is None else self.downsample(x)
        return out + res

class TCNBinaryClassifier(nn.Module):
    def __init__(self, in_channels: int = 1, channels: int = 16, dilations=(1,2,4,8,16), kernel_size: int = 3, dropout: float = 0.1):
        super().__init__()

        blocks = []
        ch_in = in_channels
        for dilation in dilations:
            block = TemporalBlock(ch_in, channels, kernel_size, dilation=dilation, droptout=dropout)
            blocks.append(block)
            ch_in = channels

        self.tcn = nn.Sequential(*blocks)
        self.classifier = nn.Linear(channels, 1)

    def forward(self, x):
        x = x.transpose(1, 2)
        feat = self.tcn(x)
        feat = feat.mean(dim=2)
        logits = self.classifier(feat)
        return logits.squeeze(1)

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

def load_trained_assets(checkpoint_path="models/spo2_tcn_1.pth", scaler_path="models/scaler_spo2.joblib"):
    utils_module = types.ModuleType('utils')
    sys.modules['utils'] = utils_module
    model_module = types.ModuleType('utils.model_tcn')
    sys.modules['utils.model_tcn'] = model_module
    setattr(model_module, 'Scaler', Scaler) 
    setattr(utils_module, 'model_tcn', model_module)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)

    model = TCNBinaryClassifier(in_channels=1)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
 
    scaler = joblib.load(scaler_path)
    
    return model, scaler