import os
import hashlib
from collections import defaultdict, Counter

ROOT = "data/cifake"
OUT = "ml/excluded_files.txt"


def hash_split(split):
    groups = defaultdict(list)
    for cls in ["REAL", "FAKE"]:
        folder = os.path.join(ROOT, split, cls)
        for f in sorted(os.listdir(folder)):
            p = os.path.join(folder, f)
            with open(p, "rb") as fh:
                h = hashlib.md5(fh.read()).hexdigest()
            groups[h].append((cls, p))
    return groups


train = hash_split("train")
test = hash_split("test")

drop = []  # (reason, class, path)

# Duplicates within train: keep the first copy, drop the rest
for h, items in train.items():
    for cls, p in items[1:]:
        drop.append(("train_dup", cls, p))

# Test images that also appear in train: drop from test
for h, items in test.items():
    if h in train:
        for cls, p in items:
            drop.append(("test_leak", cls, p))

print("Excluded by reason:", Counter(r for r, _, _ in drop))
print("Excluded by class:", Counter((r, c) for r, c, _ in drop))

with open(OUT, "w") as f:
    for reason, cls, p in drop:
        f.write(f"{reason}\t{cls}\t{os.path.normpath(p)}\n")

print(f"Wrote {len(drop)} entries to {OUT}")