import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
from load_data import load_split
from baseline import features

X_tr, y_tr, _ = load_split("train")
X_te, y_te, _ = load_split("test")
F_tr, F_te = features(X_tr), features(X_te)

scores = []
for seed in range(20):
    y_shuf = np.random.default_rng(seed).permutation(y_tr)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(F_tr, y_shuf)
    scores.append(roc_auc_score(y_te, model.predict_proba(F_te)[:, 1]))

print(f"mean {np.mean(scores):.4f}  std {np.std(scores):.4f}  "
      f"min {np.min(scores):.4f}  max {np.max(scores):.4f}")