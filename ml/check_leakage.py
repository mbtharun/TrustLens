import os
import hashlib
from collections import defaultdict

ROOT = "data/cifake"

def hash_split(split):
    groups = defaultdict(list)
    for cls in ["REAL", "FAKE"]:
        folder = os.path.join(ROOT, split, cls)
        for f in os.listdir(folder):
            p = os.path.join(folder, f)
            with open(p, "rb") as fh:
                groups[hashlib.md5(fh.read()).hexdigest()].append(p)
    return groups

train = hash_split("train")
test = hash_split("test")

shared = set(train) & set(test)
print(f"Shared hashes: {len(shared)}")
for h in list(shared)[:5]:
    print("TRAIN:", train[h])
    print("TEST: ", test[h])
    print()

dup_train = {h: ps for h, ps in train.items() if len(ps) > 1}
print(f"Duplicate groups within train: {len(dup_train)}")
for h, ps in list(dup_train.items())[:3]:
    print(ps)