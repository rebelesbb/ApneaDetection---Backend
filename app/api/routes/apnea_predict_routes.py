# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List
# import numpy as np
# import torch

# from app.model_loader import load_trained_assets

# app = FastAPI()

# class Spo2Data(BaseModel):
#     timestamps: List[int]
#     values: List[float]

# model, scaler = load_trained_assets()
# device = "cuda" if torch.cuda.is_available() else "cpu"

# @app.post("/predict")
# async def predict_apnea(data: Spo2Data):
#     print("Starting prediction...")
#     spo2_values = np.array(data.values)
#     window_size = 60
#     num_windows = len(spo2_values) // window_size
    
#     if num_windows == 0:
#         raise HTTPException(status_code=400, detail="Insufficient data for prediction. At least 60 values are required.")

#     X = spo2_values[:num_windows * window_size].reshape(num_windows, window_size, 1)
    
#     X_flattened = X.reshape(-1, 1)
#     X_scaled = scaler.transform(X_flattened).reshape(num_windows, window_size, 1)
    
#     X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(device)
#     print("Data prepared, running model inference...")
#     with torch.no_grad():
#         logits = model(X_tensor)
#         probs = torch.sigmoid(logits).cpu().numpy().flatten()
#     print("Inference completed, processing results...")

#     thr = 0.475
#     win_pred = (probs >= thr).astype(int)
    
#     n_events = np.sum(np.diff(win_pred) > 0) 
#     total_hours = len(spo2_values) / 3600
#     ahi_pred = n_events / total_hours if total_hours > 0 else 0

#     print(f"Predicted AHI: {ahi_pred}")
#     return {
#         "ahi": float(ahi_pred),
#         "predictions": win_pred.tolist(),
#     }