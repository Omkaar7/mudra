from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
import cv2
import numpy as np
import torch
from ultralytics import YOLO

app = FastAPI(title="YOLOv11 RunPod Inference")

# ==========================
# LOAD MODEL
# ==========================
MODEL_PATH = r"E:\codes\Mudra_detection\best.pt"   # place your model here
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = YOLO(MODEL_PATH)
model.to(DEVICE)

print(f"🚀 Model loaded on {DEVICE}")

# ==========================
# INFERENCE ENDPOINT
# ==========================
@app.post("/infer")
async def infer(file: UploadFile):
    image_bytes = await file.read()

    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return Response(status_code=400, content=b"Invalid image")

    results = model.predict(frame, conf=0.4, device=DEVICE)
    annotated = results[0].plot()

    _, buffer = cv2.imencode(".jpg", annotated)

    return Response(
        content=buffer.tobytes(),
        media_type="image/jpeg"
    )


@app.get("/")
def health():
    return {"status": "RunPod YOLO API running"}
