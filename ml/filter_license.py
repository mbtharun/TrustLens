import os
import pandas as pd

META = r"C:\Users\tharu\fiftyone\open-images-v7\validation\metadata\image_ids.csv"
IMG_DIR = "data/real_candidates"
OUT = "data/real_keep.csv"

meta = pd.read_csv(META, usecols=lambda c: c in {"ImageID", "License", "Author", "OriginalLandingURL"})
ids = {os.path.splitext(f)[0] for f in os.listdir(IMG_DIR)}
df = meta[meta["ImageID"].isin(ids)].copy()
print("matched images:", len(df), "of", len(ids))

print("\nLicense counts:")
print(df["License"].value_counts(dropna=False).to_string())

# Keep CC BY only: no NC (non-commercial) and no ND (no derivatives)
lic = df["License"].fillna("").str.lower()
keep = df[lic.str.contains("creativecommons.org/licenses/by/") &
          ~lic.str.contains("-nc") & ~lic.str.contains("-nd")]
print(f"\nkept (CC BY only): {len(keep)}")

keep.to_csv(OUT, index=False)
print("saved", OUT)