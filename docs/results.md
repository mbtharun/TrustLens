# Results

## Baseline: logistic regression, 11 hand-made features
- Train: 99,080 (50,000 REAL / 49,080 FAKE)
- Test: 19,622 (10,000 REAL / 9,622 FAKE)
- Accuracy 0.8238, Precision 0.8276, Recall 0.8092, F1 0.8183, ROC-AUC 0.8953
- Confusion matrix (test): [[8378, 1622], [1836, 7786]]
- Caveat: one generator only (Stable Diffusion v1.4). Measures in-distribution performance, not generalization.


## Sanity checks (baseline features)
- Label shuffle (20 seeds): mean AUC 0.510, std 0.106. Pipeline has no label leakage.
- Feature ablation (AUC on test):
  - color only: 0.641
  - texture only: 0.664
  - frequency only: 0.788
  - all features: 0.895
  - Frequency features carry most of the signal.
- JPEG re-encoding at q75:
  - original -> original: 0.895
  - q75 -> q75 (retrained): 0.896
  - original -> q75 (no retrain): 0.896
  - Signal survives uniform compression at q75. Not yet tested at harsher levels (e.g., q30) or with resizing.

  ## Cross-generator test: baseline trained on CIFAKE, tested on benchmark (ash12321, test split)
- Images resized to 32x32 (confound: resizing changes frequency content)
- Overall: acc 0.500, AUC 0.475 (n=140: 82 real, 58 AI)
- Per generator (vs real), AUC: flux 0.60 (n=9), sdxl 0.31 (n=12), nano 0.65 (n=12), seedream 0.56 (n=12), imagegbt 0.30 (n=13)
- Baseline does not transfer. Two generators are inverted. Per-generator n is too small for firm conclusions.


## CLIP ViT-L/14 linear probe (frozen features, logistic regression)
- Trained on: 1,000 REAL + 1,000 FAKE sampled from CIFAKE train (224x224, bicubic upscale)
- In-distribution (CIFAKE test, n=1000): acc 0.922, AUC 0.975
- Unseen generators (benchmark test, n=140): acc 0.679, AUC 0.793
  - flux 0.80 (n=9), sdxl 0.73 (n=12), nano 0.79 (n=12), seedream 0.88 (n=12), imagegbt 0.76 (n=13)

## Controls on the benchmark
- Baseline resized to 224x224: AUC 0.372 (still inverted; resize is not the main cause)
- CLIP on Gaussian-blurred images (sigma 2): AUC 0.820 (blur does not explain the result)

## Limitations
- CLIP trained on only 2,000 CIFAKE images, not the full 99k. Results may improve with more data.
- Benchmark is small (140 images, 9-13 per generator). Per-generator numbers are rough.
- Real images differ in source between CIFAKE (CIFAR-10) and the benchmark (mixed).
- Only one benchmark. Generalization is not yet tested on a larger or independent set.

# TrustLens: Interview Notes

## 30-second pitch
TrustLens is an AI-generated image detector. I started with a simple hand-built feature model, which scored well on its own dataset but failed on unseen generators. I then tested a frozen pretrained CLIP model on the same unseen generators and it generalized much better (AUC 0.79 vs. 0.37 to 0.47). The main thing I focused on was honest evaluation: finding leakage, checking for shortcuts, and testing on generators the model never saw.

## Architecture
- **Data:** CIFAKE (REAL from CIFAR-10, FAKE from Stable Diffusion v1.4, 32x32). Cleaned splits, with the excluded files saved to a list so they're reproducible.
- **Baseline:** 11 hand-made features (color mean/std, neighbor-pixel texture differences, FFT low/high frequency energy) into a standardized logistic regression.
- **CLIP probe:** frozen CLIP ViT-L/14 image encoder, images at 224x224, embeddings cached, logistic regression on top (the UnivFD approach).
- **Evaluation:** in-distribution test set plus a separate benchmark (140 images, 82 real and 58 AI, from 5 newer generators: FLUX, SDXL, Nano Banana Pro, SeeDream 4.5, ImageGPT).

## Data and leakage
- Training: 99,080 images (50,000 REAL, 49,080 FAKE). Test: 19,622 (10,000 REAL, 9,622 FAKE).
- Found 378 FAKE test images that were byte-identical to training images, and 920 duplicates within training. Removed both (MD5 hashes) and verified 0 overlap afterward.
- Before the fix, the accuracy numbers would have been inflated.

## Results
| Model | Test set | Acc | AUC |
|---|---|---|---|
| Baseline (11 features) | CIFAKE test, 32x32 | 0.824 | 0.895 |
| Baseline (11 features) | Benchmark, 32x32 | 0.500 | 0.475 |
| Baseline (11 features) | Benchmark, 224x224 | n/a | 0.372 |
| CLIP probe | CIFAKE test (n=1000) | 0.922 | 0.975 |
| CLIP probe | Benchmark, unseen generators | 0.679 | 0.793 |
| CLIP probe | Benchmark, blurred (sigma 2) | n/a | 0.820 |

Per generator, CLIP AUC: FLUX 0.80, SDXL 0.73, Nano Banana 0.79, SeeDream 0.88, ImageGPT 0.76.

## Challenges and how I handled them
1. **Data leakage.** Duplicate and overlapping images inflated the test score. Fixed by hashing every file and removing overlaps.
2. **Could the model be using a shortcut?**
   - Shuffled labels: mean AUC 0.51 across 20 seeds, so no label leakage.
   - Re-encoding all images as JPEG at quality 75: AUC unchanged (0.895 to 0.896), so the signal isn't a file-format artifact.
3. **The baseline doesn't generalize.** On unseen generators it's at chance (0.47 at 32x32), and two generators score below 0.5, meaning inverted. Checked at 224x224 too: 0.37, so resolution isn't the main cause.
4. **Does CLIP just detect blur?** CLIP's AUC on blurred benchmark images was 0.82, not lower, so blur doesn't explain it.

## Likely questions and answers
- **Why FFT?** It measures energy at different spatial frequencies. Generators often leave spectral patterns that differ from camera photos. It was the strongest single baseline feature (AUC 0.79 alone). I can't claim it's a universal fingerprint, since it may also reflect CIFAR-10 versus Stable Diffusion processing.
- **Why CLIP and not a CNN?** CLIP was pretrained on a huge, varied set of images, so its features capture more than one generator's artifacts. Freezing it avoids overfitting to CIFAKE. A fine-tuned CNN is the next comparison.
- **How did you prevent leakage?** Hashed every file, found 378 test-train overlaps and 920 train duplicates, removed them, and confirmed zero overlap afterward.
- **How do you know it isn't JPEG compression?** Re-encoded all images at a fixed quality. The AUC didn't change.
- **Your accuracy?** In-distribution, 92% on CIFAKE test (CLIP probe). On unseen generators, 68% accuracy and 0.79 AUC. I report the unseen-generator number as the real one.
- **What's the weakness?** The benchmark is small (140 images, 9 to 13 per generator), and the CLIP probe was trained on 2,000 CIFAKE images, not the full 99,000. Per-generator numbers are rough, and I haven't tested on an independent benchmark yet.
- **What would you do next?** Train on the full CIFAKE set (on GPU), compare with a fine-tuned CNN on the same benchmark, test on a larger multi-generator set, and add robustness tests at harsher compression.

## What not to claim
- Don't say the model "works" in general. Say it generalized better on one small benchmark.
- Don't lead with 92% or 0.975. Those are in-distribution. Lead with the unseen-generator result.
- Don't say CLIP was trained on the full dataset. It was trained on 2,000 images.


## Threshold selection (chosen on CIFAKE out-of-fold, target 5% of real flagged)
- Chosen threshold: 0.807 (5-fold OOF on 2,000 CIFAKE train images)
- Benchmark, threshold 0.807: AI caught 48/58 (0.83); real flagged AI 35/82 (0.43)
- Benchmark, threshold 0.5:   AI caught 51/58 (0.88); real flagged AI 38/82 (0.46)
- Conclusion: the CIFAKE-chosen threshold does not transfer. Real-photo false positives remain near 45% under both cutoffs, so the problem is the score distribution for real photos, not the cutoff.


## Independent real-photo check (700 images, Open Images validation)
- Source: Open Images v7 validation, license CC BY 2.0 for all images
- Near-duplicate filter: perceptual hash (Hamming <= 8) against the benchmark and 5,000 CIFAKE real images; 0 removed
- Flagged as AI at 0.5:     287/700 = 0.410 (95% CI 0.374 to 0.447)
- Flagged as AI at 0.807:   258/700 = 0.369 (95% CI 0.334 to 0.405)
- Score quantiles (10/50/90): 0.00 / 0.09 / 1.00
- Conclusion: real-photo false positives around 40% replicate on an independent set. The benchmark's real photos were not unusual.