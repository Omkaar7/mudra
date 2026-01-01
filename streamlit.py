import streamlit as st
import cv2
import requests
import numpy as np
import time

# ==========================
# CONFIG
# ==========================
RUNPOD_INFER_URL = "http://127.0.0.1:8000/infer"
CAMERA_INDEX = 0
FRAME_INTERVAL = 0.03  # seconds

st.set_page_config(page_title="YOLO RunPod Inference", layout="wide")
st.title("🎥 YOLOv11 Real-Time Inference (RunPod)")

start = st.button("▶ Start")
stop = st.button("⏹ Stop")

frame_placeholder = st.empty()

if "running" not in st.session_state:
    st.session_state.running = False

if start:
    st.session_state.running = True

if stop:
    st.session_state.running = False

# ==========================
# VIDEO LOOP
# ==========================
if st.session_state.running:
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        st.error("❌ Cannot open webcam")
    else:
        st.success("✅ Webcam started")

        while st.session_state.running:
            ret, frame = cap.read()
            if not ret:
                st.warning("⚠️ Frame read failed")
                break

            _, buffer = cv2.imencode(".jpg", frame)

            try:
                response = requests.post(
                    RUNPOD_INFER_URL,
                    files={"file": ("frame.jpg", buffer.tobytes(), "image/jpeg")},
                    timeout=10,
                )

                if response.status_code == 200:
                    annotated = cv2.imdecode(
                        np.frombuffer(response.content, np.uint8),
                        cv2.IMREAD_COLOR,
                    )
                    annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(annotated, channels="RGB")
                else:
                    st.error("Inference failed")

            except Exception as e:
                st.error(f"RunPod connection error: {e}")
                break

            time.sleep(FRAME_INTERVAL)

        cap.release()
        st.info("🛑 Camera stopped")
