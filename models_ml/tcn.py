import torch.nn as nn
import torch.nn.functional as F

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