import os
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

d = np.load("data/features/clip_cifake_train_1000.npz")
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
clf.fit(d["X"], d["y"])

os.makedirs("backend/models", exist_ok=True)
joblib.dump(clf, "backend/models/clip_probe.joblib")
print("saved backend/models/clip_probe.joblib")