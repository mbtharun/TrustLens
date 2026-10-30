# TrustLens

TrustLens detects whether an image is AI-generated or a real photo.

A frozen CLIP ViT-L/14 with a linear classifier reaches **0.79 ROC-AUC on generators it never saw during training**. A simple hand-built feature baseline scores 0.47 on the same test, which is chance. The work focuses on evaluating honestly: finding data leakage, checking for shortcuts, and testing on unseen generators.

## Results

**Unseen generators** (benchmark test set: 140 images, 82 real and 58 AI, from 5 generators; 9 to 13 AI images each):

| Model | Input | Accuracy | ROC-AUC |
|---|---|---|---|
| Hand-built features (11) | 32x32 | 0.50 | 0.47 |
| Hand-built features (11) | 224x224 | n/a | 0.37 |
| CLIP ViT-L/14 linear probe | 224x224 | 0.68 | 0.79 |
| CLIP ViT-L/14 linear probe, blurred | 224x224 | n/a | 0.82 |

Per generator, CLIP AUC (vs. real): FLUX 0.80, SDXL 0.73, Nano Banana 0.79, SeeDream 0.88, ImageGPT 0.76.

**In-distribution** (CIFAKE test set, same generator as training):

| Model | Accuracy | ROC-AUC |
|---|---|---|
| Hand-built features (11) | 0.82 | 0.90 |
| CLIP ViT-L/14 linear probe | 0.92 | 0.97 |

The in-distribution numbers are high because the training and test data share one generator. The unseen-generator numbers are the ones that matter.

## Sanity checks

- **Label shuffle:** mean AUC 0.51 over 20 random shuffles, so the pipeline has no label leakage.
- **JPEG re-encoding (quality 75):** AUC stays at 0.896, so the baseline's signal isn't a file-format artifact.
- **Blur control:** CLIP's AUC on blurred benchmark images is 0.82, so blur doesn't explain its generalization.

## Data

- **Training and in-distribution test:** [CIFAKE](https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images) (Bird & Lotfi, 2023). Real images from CIFAR-10, fake images from Stable Diffusion v1.4, all 32x32.
- **Unseen-generator test:** [ai-detector-benchmark-test-data](https://huggingface.co/datasets/ash12321/ai-detector-benchmark-test-data) (Apache 2.0). 140 images, mixed real sources, AI images from FLUX, SDXL, Nano Banana Pro, SeeDream 4.5, and ImageGPT.

Data is not included in this repo. Download it as described below.

## Limitations

- **Small benchmark.** 140 images, with 9 to 13 AI images per generator. Per-generator numbers are rough, and a difference of about 0.05 between generators is within noise.
- **Partial training set.** The CLIP probe was trained on 2,000 CIFAKE images (1,000 per class). A full-set run hit the memory limit on Colab, so it isn't reported.
- **One training generator.** CIFAKE uses only Stable Diffusion v1.4, so generalization is tested on a single unseen benchmark, not a broad range of generators.
- **Different real images.** CIFAKE's real images come from CIFAR-10, and the benchmark's come from several sources. Part of the gap could be a change in the real-image distribution, not only in the generators.
- **Resolution.** CIFAKE images are 32x32 and are upscaled to 224x224 for CLIP. The benchmark images are full size and are resized to 224x224.

Full details and the analysis behind these numbers are in [`docs/results.md`](docs/results.md) and [`docs/interview_notes.md`](docs/interview_notes.md).

## Setup

```bash
pip install torch transformers scikit-learn pyarrow pillow huggingface_hub kaggle
```

Put the data in `data/` (this folder is gitignored):

1. **CIFAKE.** Download from Kaggle into `data/cifake/` so it contains `train/` and `test/`, each with `REAL/` and `FAKE/`.
2. **Benchmark.** Download into `data/benchmark/`:
   ```bash
   python ml/download_benchmark.py
   ```

## Reproducing the results

Run all commands from the project root.

```bash
# 1. Check the splits for leakage and duplicates
python ml/check_leakage.py

# 2. Remove leaked and duplicate files (writes ml/excluded_files.txt)
python ml/clean_splits.py

# 3. Verify the cleaned splits
python ml/load_data.py

# 4. Hand-built feature baseline
python ml/baseline.py

# 5. Sanity checks: label shuffle, feature ablation, JPEG re-encoding
python ml/shuffle_repeats.py
python ml/sanity_checks.py
python ml/jpeg_check.py

# 6. Baseline on the unseen-generator benchmark
python ml/cross_generator.py

# 7. CLIP linear probe (downloads CLIP ViT-L/14, about 1.7 GB; embeddings are cached in data/features/)
python ml/clip_probe.py

# 8. Controls on the benchmark (baseline at 224x224, CLIP on blurred images)
python ml/controls.py
```

CLIP embedding runs slowly on a CPU. Using a GPU (for example, Google Colab's free T4) is much faster.

## Project structure

```
ml/        data cleaning, baseline features, CLIP probe, evaluation scripts
docs/      methodology, results, interview notes, dataset observations
notebooks/ (reserved for experiments)
data/      datasets and cached embeddings (not tracked by git)
```

## Status

- [x] Clean splits with leakage removed
- [x] Hand-built feature baseline
- [x] CLIP linear probe on unseen generators
- [ ] Probe trained on the full CIFAKE training set
- [ ] FastAPI inference endpoint
- [ ] Web demo and deployment

## License

Code: MIT (or your choice). Datasets and pretrained models keep their own licenses: CIFAKE on Kaggle, the benchmark under Apache 2.0, and CLIP ViT-L/14 from OpenAI.