import io
import os
import numpy as np
import torch
import pyarrow.parquet as pq
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, accuracy_score
from load_data import load_split

MODEL = "openai/clip-vit-large-patch14"
N_PER_CLASS_TRAIN = 1000
N_PER_CLASS_TEST = 500
BENCH = "data/benchmark/data/test-00000-of-00001.parquet"
CACHE = "data/features"
GENERATORS = ["flux", "sdxl", "nano", "seedream", "imagegbt"]

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)
model = CLIPModel.from_pretrained(MODEL).to(device).eval()
processor = CLIPProcessor.from_pretrained(MODEL)


@torch.no_grad()
def embed(pil_images, batch=32):
    out = []
    for i in range(0, len(pil_images), batch):
        inputs = processor(images=pil_images[i:i + batch], return_tensors="pt").to(device)
        pooled = model.vision_model(pixel_values=inputs["pixel_values"]).pooler_output
        feats = model.visual_projection(pooled)
        out.append(feats.cpu().numpy())
        print(f"  embedded {min(i + batch, len(pil_images))}/{len(pil_images)}", flush=True)
    return np.concatenate(out)


def balanced_sample(X, y, n, seed=0):
    rng = np.random.default_rng(seed)
    idx = np.concatenate([rng.choice(np.where(y == c)[0], n, replace=False) for c in (0, 1)])
    return X[idx], y[idx]


def cifake_embeddings(split, n):
    X, y, _ = load_split(split)
    X, y = balanced_sample(X, y, n)
    pil = [Image.fromarray(x).resize((224, 224), Image.BICUBIC) for x in X]
    return {"X": embed(pil), "y": y}


def benchmark_embeddings():
    df = pq.read_table(BENCH, columns=["image", "label", "generator"]).to_pandas()
    pil = [Image.open(io.BytesIO(d["bytes"])).convert("RGB") for d in df["image"]]
    return {"X": embed(pil),
            "y": (df["label"] == "ai").astype(int).values,
            "g": df["generator"].values.astype(str)}


def cached(name, fn):
    path = os.path.join(CACHE, f"{name}.npz")
    if os.path.exists(path):
        d = np.load(path)
        return {k: d[k] for k in d.files}
    os.makedirs(CACHE, exist_ok=True)
    d = fn()
    np.savez(path, **d)
    return d


if __name__ == "__main__":
    tr = cached(f"clip_cifake_train_{N_PER_CLASS_TRAIN}",
                lambda: cifake_embeddings("train", N_PER_CLASS_TRAIN))
    te = cached(f"clip_cifake_test_{N_PER_CLASS_TEST}",
                lambda: cifake_embeddings("test", N_PER_CLASS_TEST))
    bm = cached("clip_benchmark", benchmark_embeddings)

    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    clf.fit(tr["X"], tr["y"])

    def report(name, X, y):
        p = clf.predict_proba(X)[:, 1]
        print(f"{name}: acc {accuracy_score(y, p >= 0.5):.4f}  "
              f"AUC {roc_auc_score(y, p):.4f}  (n={len(y)})")
        return p

    report("CIFAKE test (in-distribution)", te["X"], te["y"])
    p = report("Benchmark overall (unseen generators)", bm["X"], bm["y"])

    real = bm["g"] == "real"
    for g in GENERATORS:
        m = real | (bm["g"] == g)
        print(f"  {g:9s} vs real: AUC {roc_auc_score(bm['y'][m], p[m]):.4f}  "
              f"(n_ai={np.sum(bm['g'] == g)})")