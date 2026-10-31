import fiftyone as fo
import fiftyone.zoo as foz

dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="validation",
    max_samples=700,
    label_types=[],
    shuffle=True,
    seed=0,
)

dataset.export(
    export_dir="data/real_candidates",
    dataset_type=fo.types.ImageDirectory,
)
print("exported", len(dataset), "images to data/real_candidates")