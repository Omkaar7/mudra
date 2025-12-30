from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
import cv2
import threading
import torch
import time

app = FastAPI()

model = YOLO("best.pt")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

camera = None
camera_lock = threading.Lock()
camera_running = False


def generate_frames():
    global camera, camera_running

    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)

    while camera_running:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)   # Horizontal flip
        results = model.predict(frame, conf=0.4, device=DEVICE)
        annotated = results[0].plot()

        ret, buffer = cv2.imencode(".jpg", annotated)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )

        time.sleep(0.01)  # prevent CPU hog

    # HARD STOP — ALWAYS RELEASE CAMERA
    with camera_lock:
        if camera:
            camera.release()
            camera = None
            print("📴 Camera released")


@app.post("/start")
def start_camera():
    global camera_running
    camera_running = True
    return {"status": "started"}


@app.post("/stop")
def stop_camera():
    global camera_running
    camera_running = False
    return {"status": "stopped"}


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
