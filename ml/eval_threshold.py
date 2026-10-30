import json
import numpy as np
import joblib
import pyarrow.parquet as pq

probe = joblib.load("backend/models/clip_probe.joblib")
t = json.load(open("backend/models/threshold.json"))["threshold"]

d = np.load("data/features/clip_benchmark.npz")
df = pq.read_table("data/benchmark/data/test-00000-of-00001.parquet",
                   columns=["label"]).to_pandas()
y = (df["label"] == "ai").astype(int).values
pred = probe.predict_proba(d["X"])[:, 1] >= t

print(f"Threshold: {t:.4f}")
print(f"AI caught:       {pred[y == 1].sum()}/{(y == 1).sum()} = {pred[y == 1].mean():.3f}")
print(f"Real flagged AI: {pred[y == 0].sum()}/{(y == 0).sum()} = {pred[y == 0].mean():.3f}")
print(f"Real passed:     {(~pred[y == 0]).sum()}/{(y == 0).sum()} = {1 - pred[y == 0].mean():.3f}")