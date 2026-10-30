# TrustLens

TrustLens detects whether an image is AI-generated or a real photo.

TrustLens scores how likely an image is to be AI-generated. On generators it never saw during training, the probe ranks AI images above real photos (ROC-AUC 0.79, versus 0.47 for a hand-built feature baseline). It is not a reliable real-or-fake verdict: at any threshold tested, it flags roughly 45% of real photos as AI, so the output is a ranking signal, not a decision.

A frozen CLIP ViT-L/14 with a linear classifier ranks AI images well on generators it never saw during training (**0.79 ROC-AUC**), but at the default 0.5 threshold it flags about half of real photos as AI. A simple hand-built feature baseline scores 0.47 on the same test, which is chance.


## Results

**Unseen generators** (benchmark test set: 140 images, 82 real and 58 AI, from 5 generators; 9 to 13 AI images each):

| Model | Input | Accuracy | ROC-AUC |
|---|---|---|---|
| Hand-built features (11) | 32x32 | 0.50 | 0.47 |
| Hand-built features (11) | 224x224 | n/a | 0.37 |
| CLIP ViT-L/14 linear probe | 224x224 | 0.68 | 0.79 |
| CLIP ViT-L/14 linear probe, blurred | 224x224 | n/a | 0.82 |

Per generator, CLIP AUC (vs. real): FLUX 0.80, SDXL 0.73, Nano Banana 0.79, SeeDream 0.88, ImageGPT 0.76.

## Threshold experiment

I picked a threshold on CIFAKE out-of-fold predictions, targeting 5% of real photos flagged. It was 0.807. On the benchmark it caught 83% of AI images and flagged 43% of real photos. The default 0.5 flagged 46%. The CIFAKE-chosen threshold did not transfer. The problem is the score distribution for real photos, not the cutoff.

**Per-class results at threshold 0.5** (CLIP probe, unseen generators):

| Class | Correct | Rate |
|---|---|---|
| AI images (n=58) | 51 | 88% |
| Real photos (n=82) | 44 | 54% |

The overall accuracy of 68% averages these two rates and hides the imbalance. Nearly half of real photos are flagged as AI.

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

- **False positives on real photos.** At threshold 0.5, 38 of 82 real photos are flagged as AI. Any product built on this model needs a different threshold, chosen on CIFAKE validation data rather than the benchmark.
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


## API

Serve the probe with FastAPI:

```bash
python ml/save_probe.py          # saves backend/models/clip_probe.joblib
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs and use `POST /analyze` to upload an image. The endpoint returns `probability_ai` and a label at threshold 0.5. Its scores match the offline evaluation on the same images.

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

# 9. Check that the API's preprocessing matches the cached evaluation
python ml/check_probe_on_cache.py
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
- [x] Threshold selected on CIFAKE and evaluated once on the benchmark (does not transfer)
- [x] FastAPI endpoint (matches offline evaluation)
- [ ] Probe trained on the full CIFAKE training set
- [ ] FastAPI inference endpoint
- [ ] Web demo and deployment

## License

Code: MIT (or your choice). Datasets and pretrained models keep their own licenses: CIFAKE on Kaggle, the benchmark under Apache 2.0, and CLIP ViT-L/14 from OpenAI.