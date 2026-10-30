The model ranks AI images well on unseen generators, but at the default threshold it flags about half of real photos as AI. So it's not ready for a user-facing verdict, and I measured that rather than hiding it.

| CLIP probe, unseen generators | AI caught 88% (51/58), real passed 54% (44/82) | 0.79 |

5. **API preprocessing mismatch.** The API first squashed every image to 224x224, which distorted non-square photos. Two real images scored 0.52 and 0.98 through the API, versus 0.85 and 0.86 in the evaluation. I changed the API to use CLIP's own processor, and now the API scores match the evaluation exactly.
6. **Threshold calibration.** The probe ranks well (AUC 0.79) but its 0.5 threshold is miscalibrated for real photos. The fix is to pick the threshold on CIFAKE validation data, not on the benchmark, to avoid tuning on the test set.

- **Your accuracy?** On unseen generators, the probe catches 88% of AI images and passes 54% of real photos at threshold 0.5. The overall 68% hides that imbalance, so I report the per-class numbers. The AUC of 0.79 measures ranking, not a yes-or-no verdict.
- **Would you ship this?** Not as a verdict. It's a ranking signal. Before a product, I'd choose the threshold on held-out CIFAKE data, test on more generators, and add an "uncertain" band for the middle scores.

- Don't quote 68% accuracy alone. It averages a strong class and a weak one.
- Don't say the model is accurate on real photos. It passes only about half of them.

Not as a verdict. I tested a threshold chosen on training data and it did not transfer: real-photo false positives stayed near 45%. So I shipped it as a ranking score, and I'd need a larger benchmark and a better real-photo training distribution before any verdict.