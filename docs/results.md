# Results

## Baseline: logistic regression, 11 hand-made features
- Train: 99,080 (50,000 REAL / 49,080 FAKE)
- Test: 19,622 (10,000 REAL / 9,622 FAKE)
- Accuracy 0.8238, Precision 0.8276, Recall 0.8092, F1 0.8183, ROC-AUC 0.8953
- Confusion matrix (test): [[8378, 1622], [1836, 7786]]
- Caveat: one generator only (Stable Diffusion v1.4). Measures in-distribution performance, not generalization.