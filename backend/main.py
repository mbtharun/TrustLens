import io
import json
import joblib
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

MODEL = "openai/clip-vit-large-patch14"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024

THRESHOLD = json.load(open("backend/models/threshold.json"))["threshold"]

device = "cuda" if torch.cuda.is_available() else "cpu"
clip = CLIPModel.from_pretrained(MODEL).to(device).eval()
processor = CLIPProcessor.from_pretrained(MODEL)
probe = joblib.load("backend/models/clip_probe.joblib")

app = FastAPI(title="TrustLens")


@app.get("/health")
def health():
    return {"status": "ok", "device": device}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Upload a JPG, PNG, or WebP image.")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File is larger than 10 MB.")
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Could not read this image.")

    with torch.no_grad():
        pix = processor(images=img, return_tensors="pt")["pixel_values"].to(device)
        pooled = clip.vision_model(pixel_values=pix).pooler_output
        feats = clip.visual_projection(pooled).cpu().numpy()

    prob_ai = float(probe.predict_proba(feats)[0, 1])
    return {
        "prediction": "likely_ai" if prob_ai >= THRESHOLD else "likely_real",
        "probability_ai": round(prob_ai, 4),
        "threshold": round(THRESHOLD, 4),
        "model": "CLIP ViT-L/14 linear probe",
        "note": "Probabilistic estimate, not proof. Threshold chosen on CIFAKE data only; see docs for benchmark results.",
    }