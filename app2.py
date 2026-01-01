from fastapi import FastAPI, UploadFile, File
from typing import List
import cv2
import numpy as np
import base64
import torch
from ultralytics import YOLO
import logging
import time

# ==========================
# LOGGING CONFIG
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("MudraAI")

# ==========================
# APP INIT
# ==========================
app = FastAPI(title="MudraAI YOLOv11 Backend")

# ==========================
# MODEL LOAD
# ==========================
MODEL_PATH = "best.pt"
device = "cuda" if torch.cuda.is_available() else "cpu"

logger.info("🚀 Starting MudraAI Backend...")
logger.info(f"📦 Loading YOLO model from: {MODEL_PATH}")
logger.info(f"🧠 Using device: {device}")

model = YOLO(MODEL_PATH).to(device)

logger.info("✅ Model loaded successfully")

# ==========================
# HEALTH CHECK
# ==========================
@app.get("/")
async def health_check():
    logger.info("🩺 Health check ping received")
    return {"status": "healthy", "message": "MudraAI Backend is running"}

# ==========================
# BATCH INFERENCE
# ==========================
@app.post("/infer_batch")
async def infer_batch(files: List[UploadFile] = File(...)):
    request_start = time.time()
    logger.info(f"📥 Received infer_batch request with {len(files)} files")

    frames = []

    # --------------------------
    # Decode images
    # --------------------------
    for idx, file in enumerate(files):
        data = await file.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            logger.warning(f"⚠️ Frame {idx} could not be decoded")
            continue

        frames.append(img)
        logger.info(f"🖼️ Frame {idx} decoded successfully | shape={img.shape}")

    if not frames:
        logger.error("❌ No valid frames received")
        return {"frames": [], "msg": "No valid frames received"}

    logger.info(f"✅ Total valid frames: {len(frames)}")

    # --------------------------
    # Batch inference
    # --------------------------
    infer_start = time.time()
    logger.info("🤖 Starting YOLO batch inference")

    results = model.predict(
        source=frames,
        conf=0.4,
        device=device,
        verbose=False
    )

    infer_time = time.time() - infer_start
    logger.info(f"⚡ Inference completed in {infer_time:.2f}s")

    # --------------------------
    # Encode results
    # --------------------------
    processed_b64 = []

    for idx, r in enumerate(results):
        annotated_img = r.plot()
        success, buffer = cv2.imencode(
            ".jpg",
            annotated_img,
            [cv2.IMWRITE_JPEG_QUALITY, 85]
        )

        if not success:
            logger.warning(f"⚠️ Encoding failed for frame {idx}")
            continue

        img_str = base64.b64encode(buffer).decode("utf-8")
        processed_b64.append(img_str)

        logger.info(f"📦 Frame {idx} annotated & encoded")

    total_time = time.time() - request_start
    logger.info(
        f"✅ Request completed | Frames={len(processed_b64)} | Total time={total_time:.2f}s"
    )

    return {"frames": processed_b64}

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    import uvicorn
    logger.info("🌐 Starting Uvicorn server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
