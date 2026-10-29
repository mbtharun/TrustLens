import os, random
from PIL import Image

random.seed(0)
root = "data/cifake/train"

def sheet(cls, out):
    files = [os.path.join(root, cls, f) for f in os.listdir(os.path.join(root, cls))]
    picks = random.sample(files, 20)
    grid = Image.new("RGB", (5 * 256, 4 * 256), "white")
    for i, p in enumerate(picks):
        img = Image.open(p).convert("RGB").resize((256, 256), Image.NEAREST)
        grid.paste(img, ((i % 5) * 256, (i // 5) * 256))
    grid.save(out)

sheet("REAL", "docs/real_sheet.png")
sheet("FAKE", "docs/fake_sheet.png")
print("Saved docs/real_sheet.png and docs/fake_sheet.png")