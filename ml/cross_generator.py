import io
import numpy as np
import pyarrow.parquet as pq
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, accuracy_score
from load_data import load_split
from baseline import features

BENCH = "data/benchmark/data/test-00000-of-00001.parquet"
GENERATORS = ["flux", "sdxl", "nano", "seedream", "imagegbt"]


def load_benchmark(path):
    df = pq.read_table(path, columns=["image", "label", "generator"]).to_pandas()
    X = np.stack([
        np.asarray(
            Image.open(io.BytesIO(d["bytes"])).convert("RGB").resize((32, 32), Image.BICUBIC)
        )
        for d in df["image"]
    ])
    y = (df["label"] == "ai").astype(int).values
    return X, y, df["generator"].values


if __name__ == "__main__":
    X_tr, y_tr, _ = load_split("train")
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(features(X_tr), y_tr)

    X_b, y_b, gen = load_benchmark(BENCH)
    prob = model.predict_proba(features(X_b))[:, 1]
    pred = (prob >= 0.5).astype(int)

    print(f"Overall: acc {accuracy_score(y_b, pred):.4f}  AUC {roc_auc_score(y_b, prob):.4f}  (n={len(y_b)})")
    real = gen == "real"
    for g in GENERATORS:
        m = real | (gen == g)
        print(f"{g:9s} vs real: acc {accuracy_score(y_b[m], pred[m]):.4f}  "
              f"AUC {roc_auc_score(y_b[m], prob[m]):.4f}  (n_ai={np.sum(gen == g)})")