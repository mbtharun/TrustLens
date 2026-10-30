import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix)
from load_data import load_split


def features(X):
    X = X.astype(np.float32) / 255.0
    feats = []
    # Color statistics per channel: mean, std
    feats.append(X.mean(axis=(1, 2)))
    feats.append(X.std(axis=(1, 2)))
    # Grayscale for texture and frequency
    gray = X.mean(axis=3)
    # Local texture: mean absolute difference between neighboring pixels
    dx = np.abs(np.diff(gray, axis=2)).mean(axis=(1, 2))
    dy = np.abs(np.diff(gray, axis=1)).mean(axis=(1, 2))
    feats.append(np.stack([dx, dy], axis=1))
    # Frequency: energy in low vs high spatial frequencies via 2D FFT
    spec = np.abs(np.fft.fftshift(np.fft.fft2(gray), axes=(1, 2)))
    h, w = gray.shape[1], gray.shape[2]
    yy, xx = np.meshgrid(np.arange(h) - h // 2, np.arange(w) - w // 2, indexing="ij")
    radius = np.sqrt(yy ** 2 + xx ** 2)
    low = spec[:, radius < 4].mean(axis=1)
    high = spec[:, radius >= 12].mean(axis=1)
    feats.append(np.stack([low, high, high / (low + 1e-8)], axis=1))
    return np.concatenate(feats, axis=1)


if __name__ == "__main__":
    X_tr, y_tr, _ = load_split("train")
    X_te, y_te, _ = load_split("test")

    F_tr = features(X_tr)
    F_te = features(X_te)
    print("feature shape:", F_tr.shape)

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(F_tr, y_tr)

    prob = model.predict_proba(F_te)[:, 1]
    pred = (prob >= 0.5).astype(int)

    print(f"Accuracy:  {accuracy_score(y_te, pred):.4f}")
    print(f"Precision: {precision_score(y_te, pred):.4f}")
    print(f"Recall:    {recall_score(y_te, pred):.4f}")
    print(f"F1:        {f1_score(y_te, pred):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_te, prob):.4f}")
    print("Confusion matrix (rows = actual REAL/FAKE, cols = predicted REAL/FAKE):")
    print(confusion_matrix(y_te, pred))