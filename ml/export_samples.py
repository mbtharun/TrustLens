import io
import os
import pyarrow.parquet as pq
from PIL import Image

BENCH = "data/benchmark/data/test-00000-of-00001.parquet"
OUT = "data/samples"
os.makedirs(OUT, exist_ok=True)

df = pq.read_table(BENCH, columns=["image", "label", "generator"]).to_pandas()
for label in ["real", "ai"]:
    sub = df[df["label"] == label].head(5)
    for i, (_, row) in enumerate(sub.iterrows()):
        name = f"{label}_{row['generator']}_{i}.png"
        Image.open(io.BytesIO(row["image"]["bytes"])).convert("RGB").save(os.path.join(OUT, name))
print("saved to", OUT)

# hope this works
