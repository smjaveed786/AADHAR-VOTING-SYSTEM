
import torch
import os

model_path = "../models/liveness_detector_production.pth"
if not os.path.exists(model_path):
    print(f"Model not found at {model_path}")
    exit(1)

try:
    checkpoint = torch.load(model_path, map_location='cpu')
    if 'model_state_dict' in checkpoint:
        keys = list(checkpoint['model_state_dict'].keys())
    else:
        keys = list(checkpoint.keys())
    
    print("First 10 keys:")
    for k in keys[:10]:
        print(k)
        
except Exception as e:
    print(f"Error: {e}")
