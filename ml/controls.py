import io
import numpy as np
import pyarrow.parquet as pq
from PIL import Image, ImageFilter
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
from load_data import load_split
from baseline import features
from clip_probe import cached, embed, benchmark_embeddings, BENCH

GENS = ["flux", "sdxl", "nano", "seedream", "imagegbt"]


def auc_by_gen(y, g, score):
    out = {}
    real = g == "real"
    for gen in GENS:
        m = real | (g == gen)
        out[gen] = roc_auc_score(y[m], score[m])
    return roc_auc_score(y, score), out


# 1. Baseline trained on CIFAKE, benchmark resized to 224x224 (matches CLIP's input size)
X_tr, y_tr, _ = load_split("train")
base = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
base.fit(features(X_tr), y_tr)

df = pq.read_table(BENCH, columns=["image", "label", "generator"]).to_pandas()
y = (df["label"] == "ai").astype(int).values
g = df["generator"].values.astype(str)
pil = [Image.open(io.BytesIO(d["bytes"])).convert("RGB") for d in df["image"]]

X224 = np.stack([np.asarray(im.resize((224, 224), Image.BICUBIC)) for im in pil])
s = base.predict_proba(features(X224))[:, 1]
overall, per = auc_by_gen(y, g, s)
print(f"[1] Baseline @224:        overall AUC {overall:.4f} | " +
      " ".join(f"{k} {v:.2f}" for k, v in per.items()))

# 2. CLIP on blurred benchmark images (sharpness control)
blurred = [im.resize((224, 224), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
           for im in pil]
blur_emb = cached("clip_benchmark_blurred", lambda: {"X": embed(blurred), "y": y, "g": g})

# CLIP probe trained on CIFAKE embeddings (same as clip_probe.py)
tr = cached("clip_cifake_train_1000", lambda: None)
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
clf.fit(tr["X"], tr["y"])
s_blur = clf.predict_proba(blur_emb["X"])[:, 1]
overall, per = auc_by_gen(y, g, s_blur)
print(f"[2] CLIP, blurred bench:  overall AUC {overall:.4f} | " +
      " ".join(f"{k} {v:.2f}" for k, v in per.items()))