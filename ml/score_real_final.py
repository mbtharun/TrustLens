import os
import math
import numpy as np
import pandas as pd
import joblib
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

MODEL = "openai/clip-vit-large-patch14"
device = "cuda" if torch.cuda.is_available() else "cpu"
clip = CLIPModel.from_pretrained(MODEL).to(device).eval()
proc = CLIPProcessor.from_pretrained(MODEL)
probe = joblib.load("backend/models/clip_probe.joblib")

df = pd.read_csv("data/real_final.csv")
paths = [os.path.join("data/real_candidates", f"{i}.jpg") for i in df["ImageID"]]

scores = []
with torch.no_grad():
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB")
        pix = proc(images=img, return_tensors="pt")["pixel_values"].to(device)
        f = clip.visual_projection(clip.vision_model(pixel_values=pix).pooler_output)
        scores.append(float(probe.predict_proba(f.cpu().numpy())[0, 1]))
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(paths)}", flush=True)

s = np.array(scores)
n = len(s)

def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

print(f"\nn = {n} real photos (Open Images, CC BY 2.0, dedup'd)")
for t in (0.5, 0.8072):
    k = int((s >= t).sum())
    lo, hi = wilson(k, n)
    print(f"threshold {t}: flagged {k}/{n} = {k/n:.3f}  (95% CI {lo:.3f} to {hi:.3f})")
print("score quantiles 10/50/90:", np.round(np.quantile(s, [0.1, 0.5, 0.9]), 4))

pd.DataFrame({"ImageID": df["ImageID"], "probability_ai": s}).to_csv(
    "data/real_final_scores.csv", index=False)
print("saved data/real_final_scores.csv")