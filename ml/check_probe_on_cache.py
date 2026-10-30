import numpy as np
import joblib
import pyarrow.parquet as pq
from sklearn.metrics import roc_auc_score

probe = joblib.load("backend/models/clip_probe.joblib")
d = np.load("data/features/clip_benchmark.npz")
df = pq.read_table("data/benchmark/data/test-00000-of-00001.parquet",
                   columns=["label"]).to_pandas()

y = (df["label"] == "ai").astype(int).values
p = probe.predict_proba(d["X"])[:, 1]
pred = (p >= 0.5).astype(int)

real_idx = np.where(y == 0)[0]
ai_idx = np.where(y == 1)[0]

print("First 5 real images (compare with API):")
for k, i in enumerate(real_idx[:5]):
    print(f"  real_real_{k}: {p[i]:.4f}")

print(f"Real accuracy (n={len(real_idx)}): {np.mean(pred[real_idx] == 0):.3f}")
print(f"AI accuracy   (n={len(ai_idx)}): {np.mean(pred[ai_idx] == 1):.3f}")
print(f"Overall AUC: {roc_auc_score(y, p):.4f}")