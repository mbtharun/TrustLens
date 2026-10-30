# TrustLens

TrustLens is an AI-image detection project built around one question: **does a model still work on images from generators it never saw?** I built a baseline, tested it, found that it failed, then tested a pretrained CLIP model on the same images. The result is a clear ranking signal and a documented limit, with the evaluation designed to show both.

## What I found

- **Ranking works on unseen generators.** A frozen CLIP ViT-L/14 with a linear classifier reaches **0.79 ROC-AUC** on generators it never trained on, versus 0.47 for a hand-built feature baseline.
- **Real-photo false positives are the main limit.** On an independent set of 700 real photos, the model flags about 41% as AI at the default threshold. That's the number a product would have to solve before giving any verdict.
- **So TrustLens outputs a score, not a verdict.** The API returns a probability and a note saying so.

## How the evaluation was built

Most of the work went into making sure the numbers can be trusted:

- **Leakage removed.** I hashed every file and found 378 test images that were byte-identical to training images, plus 920 duplicates in training. Both were removed and the exclusions are saved, so the splits are reproducible.
- **Sanity checks.** Shuffled labels give AUC 0.51 (no label leakage). Re-encoding images as JPEG leaves the baseline's AUC unchanged, so it isn't learning file formats.
- **Threshold chosen without the test set.** I picked the cutoff on CIFAKE out-of-fold predictions, targeting 5% false positives, and scored the benchmark once. It didn't transfer, and that result is reported as-is.
- **Independent check.** 700 Open Images photos, all CC BY 2.0, filtered against the benchmark and CIFAKE for near-duplicates.

## Results

### Unseen generators

Benchmark: 140 images (82 real, 58 AI) from five generators, with 9 to 13 AI images each.

| Model | Input | Accuracy | ROC-AUC |
|---|---|---|---|
| Hand-built features (11) | 32x32 | 0.50 | 0.47 |
| Hand-built features (11) | 224x224 | n/a | 0.37 |
| CLIP ViT-L/14 linear probe | 224x224 | 0.68 | 0.79 |
| CLIP ViT-L/14 linear probe, blurred | 224x224 | n/a | 0.82 |

Per generator, CLIP AUC against real photos: FLUX 0.80, SDXL 0.73, Nano Banana 0.79, SeeDream 0.88, ImageGPT 0.76.

**Per class at threshold 0.5:**

| Class | Correct | Rate |
|---|---|---|
| AI images (n=58) | 51 | 88% |
| Real photos (n=82) | 44 | 54% |

The 68% overall accuracy averages these two rates, so I report the per-class numbers alongside it.

### Independent real-photo check

| Threshold | Real photos flagged as AI | 95% CI |
|---|---|---|
| 0.50 | 287 / 700 = 41.0% | 37.4% to 44.7% |
| 0.807 | 258 / 700 = 36.9% | 33.4% to 40.5% |

The score distribution is nearly binary: the 10th percentile is 0.00 and the 90th is 1.00, so the model is near-certain on most images and often wrong on real photos.

### Threshold experiment

Chosen on CIFAKE out-of-fold predictions at 0.807, targeting 5% false positives. On the benchmark it caught 83% of AI images and flagged 43% of real photos. The default 0.5 flagged 46%. The problem is the score distribution for real photos, not the cutoff.

### In-distribution

CIFAKE test set, same generator as training:

| Model | Accuracy | ROC-AUC |
|---|---|---|
| Hand-built features (11) | 0.82 | 0.90 |
| CLIP ViT-L/14 linear probe | 0.92 | 0.97 |

These are high because training and test share one generator. The unseen-generator numbers are the ones that matter.

## Limitations

- **Real-photo false positives.** About 40% on the independent set and 43% on the benchmark. Not suitable for a real-or-fake verdict.
- **Small benchmark.** 140 images, so per-generator numbers are rough, and differences near 0.05 are within noise.
- **Partial training set.** The probe was trained on 2,000 CIFAKE images. A full-set run hit the Colab memory limit and isn't reported.
- **One training generator.** CIFAKE uses only Stable Diffusion v1.4.
- **Real-image source mismatch.** CIFAKE's real images come from CIFAR-10. The other real-photo sources differ, which may explain part of the gap.
- **Resolution.** CIFAKE is 32x32, upscaled to 224x224. The other sets are full size, resized to 224x224.
- **Partial duplicate check.** The filter compared Open Images against the full benchmark and 5,000 of CIFAKE's real images.

## Next steps

- Choose a threshold on a validation set that includes real photos from several sources.
- Train on a larger, more varied real-photo set and re-run the independent check.
- Add a web demo and deploy the API.

Full details are in [`docs/results.md`](docs/results.md) and [`docs/interview_notes.md`](docs/interview_notes.md).

## Data

- **Training and in-distribution test:** [CIFAKE](https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images) (Bird & Lotfi, 2023). The Kaggle page lists the license as "other"; check before reuse.
- **Unseen-generator benchmark:** [ai-detector-benchmark-test-data](https://huggingface.co/datasets/ash12321/ai-detector-benchmark-test-data) (Apache 2.0).
- **Independent real photos:** [Open Images v7](https://storage.googleapis.com/openimages/web/index.html) validation split, 700 images, all CC BY 2.0.

Data is not included in this repo. See Setup.

## API

```bash
python ml/save_probe.py          # saves backend/models/clip_probe.joblib
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs and use `POST /analyze`. It returns `probability_ai` and a note that the result is a ranking, not a verdict. Scores match the offline evaluation.

## Setup

```bash
pip install torch transformers scikit-learn pyarrow pillow huggingface_hub kaggle joblib
pip install fastapi uvicorn python-multipart fiftyone imagehash
```

Put data in `data/` (gitignored):

1. **CIFAKE:** download from Kaggle into `data/cifake/`, with `train/` and `test/`, each containing `REAL/` and `FAKE/`.
2. **Benchmark:** `python ml/download_benchmark.py`
3. **Open Images (for the independent check):** `python ml/download_openimages.py`, then `python ml/filter_license.py` and `python ml/dedupe_real.py`.

## Reproducing the results

Run from the project root.

```bash
python ml/check_leakage.py          # 1. find leakage and duplicates
python ml/clean_splits.py           # 2. remove them (writes ml/excluded_files.txt)
python ml/load_data.py              # 3. verify the cleaned splits
python ml/baseline.py               # 4. hand-built feature baseline
python ml/shuffle_repeats.py        # 5. sanity checks
python ml/sanity_checks.py
python ml/jpeg_check.py
python ml/cross_generator.py        # 6. baseline on the unseen-generator benchmark
python ml/clip_probe.py             # 7. CLIP probe (embeddings cached in data/features/)
python ml/controls.py               # 8. benchmark controls (224x224 baseline, blurred CLIP)
python ml/check_probe_on_cache.py   # 9. API preprocessing matches the evaluation
python ml/pick_threshold.py         # 10. threshold from CIFAKE out-of-fold
python ml/eval_threshold.py         # 10. benchmark, evaluated once
python ml/score_real_final.py       # 11. independent real-photo check
```

CLIP embedding is slow on a CPU. A free Colab T4 GPU is much faster.

## Project structure

```
ml/        data cleaning, baseline, CLIP probe, evaluation
backend/   FastAPI service and saved probe
docs/      methodology, results, interview notes
data/      datasets and cached embeddings (not tracked)
```

## Status

- [x] Leakage removed and splits verified
- [x] Hand-built baseline, sanity checks, and controls
- [x] CLIP probe evaluated on unseen generators
- [x] Threshold chosen on CIFAKE, evaluated once on the benchmark
- [x] Independent real-photo check (700 Open Images)
- [x] FastAPI endpoint, matches offline evaluation
- [ ] Probe trained on the full CIFAKE training set
- [ ] Web demo and deployment

## License

Code: MIT (or your choice). Datasets and models keep their own licenses: CIFAKE on Kaggle (check the page), the benchmark under Apache 2.0, Open Images photos under CC BY 2.0, and CLIP ViT-L/14 from OpenAI.