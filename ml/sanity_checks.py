import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
from load_data import load_split
from baseline import features

X_tr, y_tr, _ = load_split("train")
X_te, y_te, _ = load_split("test")
F_tr = features(X_tr)
F_te = features(X_te)


def auc(cols, labels_train=y_tr):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(F_tr[:, cols], labels_train)
    prob = model.predict_proba(F_te[:, cols])[:, 1]
    return roc_auc_score(y_te, prob)


all_cols = list(range(F_tr.shape[1]))

# 1. Label shuffle: AUC should be near 0.5
rng = np.random.default_rng(0)
print(f"Shuffled labels, all features: AUC {auc(all_cols, rng.permutation(y_tr)):.4f}")

# 2. Feature ablation: which group carries the signal?
groups = {
    "color (mean, std)": [0, 1, 2, 3, 4, 5],
    "texture (neighbor diffs)": [6, 7],
    "frequency (FFT energy)": [8, 9, 10],
}
for name, cols in groups.items():
    print(f"{name:28s} AUC {auc(cols):.4f}")
print(f"{'all features':28s} AUC {auc(all_cols):.4f}")