import os
import hashlib
from collections import Counter
import numpy as np
from PIL import Image

ROOT = "data/cifake"
CLASSES = {"REAL": 0, "FAKE": 1}

EXCLUDED = set()
if os.path.exists("ml/excluded_files.txt"):
    with open("ml/excluded_files.txt") as fh:
        EXCLUDED = {line.split("\t")[2].strip() for line in fh}


def load_split(split):
    X, y, paths = [], [], []
    for cls, label in CLASSES.items():
        folder = os.path.join(ROOT, split, cls)
        for f in sorted(os.listdir(folder)):
            p = os.path.join(folder, f)
            if os.path.normpath(p) in EXCLUDED:
                continue
            X.append(np.asarray(Image.open(p).convert("RGB")))
            y.append(label)
            paths.append(p)
    return np.stack(X), np.array(y), paths


def file_hash(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


if __name__ == "__main__":
    data = {}
    for split in ["train", "test"]:
        X, y, paths = load_split(split)
        data[split] = (X, y, paths)
        print(f"\n{split}")
        print(f"  X shape: {X.shape}, dtype: {X.dtype}")
        print(f"  REAL: {np.sum(y == 0)}, FAKE: {np.sum(y == 1)}")
        sizes = Counter(Image.open(p).size for p in paths[:2000])
        print(f"  image sizes (first 2000): {dict(sizes)}")

    print("\nAverage file size in bytes, train:")
    for cls in CLASSES:
        cls_paths = [p for p in data["train"][2] if os.path.basename(os.path.dirname(p)) == cls]
        avg = sum(os.path.getsize(p) for p in cls_paths) // len(cls_paths)
        print(f"  {cls}: {avg}")

    train_hashes = {file_hash(p) for p in data["train"][2]}
    test_hashes = {file_hash(p) for p in data["test"][2]}
    print(f"\nUnique files in train: {len(train_hashes)} of {len(data['train'][2])}")
    print(f"Files shared between train and test: {len(train_hashes & test_hashes)}")