Dataset: CIFAKE (Bird & Lotfi, 2023), 32×32 images, REAL from CIFAR-10, FAKE from Stable Diffusion v1.4. Include the license from Kaggle.
Original split: 100k train / 20k test.
Leakage found: 378 FAKE test images were byte-identical to train images.
Duplicates in train: 920 identical FAKE copies, removed.
Final counts (above).
Limitation: only one generator, so this measures in-distribution performance, not generalization to unseen generators.