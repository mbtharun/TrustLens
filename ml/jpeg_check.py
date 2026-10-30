import io
import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
from load_data import load_split
from baseline import features


def reencode(X, quality):
    out = np.empty_like(X)
    for i, img in enumerate(X):
        buf = io.BytesIO()
        Image.fromarray(img).save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        out[i] = np.asarray(Image.open(buf).convert("RGB"))
    return out


def fit_auc(F_tr, y_tr, F_te, y_te):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(F_tr, y_tr)
    return roc_auc_score(y_te, model.predict_proba(F_te)[:, 1])


X_tr, y_tr, _ = load_split("train")
X_te, y_te, _ = load_split("test")

F_tr = features(X_tr)
F_te = features(X_te)

# A. Original images, as before
print(f"Original -> original:              AUC {fit_auc(F_tr, y_tr, F_te, y_te):.4f}")

# B. Same JPEG quality on both splits, retrain
X_tr_q = reencode(X_tr, 75)
X_te_q = reencode(X_te, 75)
F_tr_q, F_te_q = features(X_tr_q), features(X_te_q)
print(f"JPEG q75 -> JPEG q75 (retrained):  AUC {fit_auc(F_tr_q, y_tr, F_te_q, y_te):.4f}")

# C. Train on originals, test on re-encoded (robustness to compression)
print(f"Original -> JPEG q75 (no retrain): AUC {fit_auc(F_tr, y_tr, F_te_q, y_te):.4f}")