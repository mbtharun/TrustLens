import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict

TARGET_FPR = 0.05

d = np.load("data/features/clip_cifake_train_1000.npz")
X, y = d["X"], d["y"]

clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
oof = cross_val_predict(
    clf, X, y,
    cv=StratifiedKFold(5, shuffle=True, random_state=0),
    method="predict_proba",
)[:, 1]

real = oof[y == 0]
threshold = float(np.quantile(real, 1 - TARGET_FPR))
fpr = float(np.mean(real >= threshold))
tpr = float(np.mean(oof[y == 1] >= threshold))

print(f"Threshold: {threshold:.4f}")
print(f"CIFAKE out-of-fold: real flagged {fpr:.3f}, AI caught {tpr:.3f}")

with open("backend/models/threshold.json", "w") as f:
    json.dump({
        "threshold": threshold,
        "target_fpr": TARGET_FPR,
        "source": "5-fold out-of-fold on CIFAKE train subset (2000 images)",
    }, f, indent=2)
print("saved backend/models/threshold.json")