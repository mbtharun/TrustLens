import os
import io
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from PIL import Image
import imagehash

KEEP = "data/real_keep.csv"
OUT = "data/real_final.csv"
BENCH = "data/benchmark/data/test-00000-of-00001.parquet"
CIFAKE_REAL = "data/cifake/train/REAL"
THRESH = 8  # Hamming distance; <= 8 on a 64-bit hash counts as near-duplicate

def phash(img):
    return imagehash.phash(img.convert("RGB"))

# Hashes of existing images we must not overlap with
ref = []
df_b = pq.read_table(BENCH, columns=["image"]).to_pandas()
for d in df_b["image"]:
    ref.append(phash(Image.open(io.BytesIO(d["bytes"]))))
for f in os.listdir(CIFAKE_REAL)[:5000]:  # CIFAKE REAL is 32x32; sample is enough
    ref.append(phash(Image.open(os.path.join(CIFAKE_REAL, f))))
print("reference hashes:", len(ref))

keep = pd.read_csv(KEEP)
flags = []
for _, row in keep.iterrows():
    p = os.path.join("data/real_candidates", f"{row['ImageID']}.jpg")
    try:
        h = phash(Image.open(p))
    except Exception:
        flags.append(True)
        continue
    dup = any((h - r) <= THRESH for r in ref)
    flags.append(dup)

keep["near_dup"] = flags
print("near-duplicates:", int(sum(flags)))
final = keep[~keep["near_dup"]]
print("final real candidates:", len(final))
final.to_csv(OUT, index=False)
print("saved", OUT)