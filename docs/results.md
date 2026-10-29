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