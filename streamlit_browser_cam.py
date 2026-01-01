import streamlit as st
import requests
import time
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode

# ================= CONFIG =================
BACKEND_URL = "https://8knckq5xwxalxn-8000.proxy.runpod.net/infer_batch"
CAPTURE_SECONDS = 3
FPS = 5
TOTAL_FRAMES = CAPTURE_SECONDS * FPS

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# ================= PROCESSOR =================
class VideoProcessor:
    def __init__(self):
        self.latest_frame = None

    def recv(self, frame):
        # This runs in a separate thread
        img = frame.to_ndarray(format="bgr24")
        self.latest_frame = img
        return frame

# ================= PAGE =================
st.set_page_config(page_title="Kathak Mudra Detection", layout="wide")
st.title("Kathak Mudra Detection")

# Initialize WebRTC with the processor
ctx = webrtc_streamer(
    key="camera",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

st.divider()

# ================= CAPTURE LOGIC =================
if st.button("🚀 Capture 5 Seconds & Infer", use_container_width=True):
    
    if not ctx.state.playing:
        st.error("❌ Please start the camera first (click Start/Play).")
        st.stop()

    status = st.empty()
    progress_bar = st.progress(0)
    
    captured_images = []
    
    status.info(f"📸 Capturing {TOTAL_FRAMES} frames...")
    
    for i in range(TOTAL_FRAMES):
        # Access the frame stored in the processor
        if ctx.video_processor and ctx.video_processor.latest_frame is not None:
            img = ctx.video_processor.latest_frame
            
            # Encode frame to JPEG
            ok, buf = cv2.imencode(".jpg", img)
            if ok:
                captured_images.append(buf.tobytes())
            
            # Update UI
            progress_bar.progress((i + 1) / TOTAL_FRAMES)
            status.text(f"Captured {len(captured_images)}/{TOTAL_FRAMES}")
        else:
            status.warning("⚠️ Waiting for video processor...")
            time.sleep(0.5)
            continue
            
        # Control the capture frequency
        time.sleep(1 / FPS)

    if len(captured_images) == 0:
        st.error("❌ Failed to capture any frames. Is your camera feed active?")
        st.stop()

    # ---------- SEND TO BACKEND ----------
    status.info("📤 Sending burst to backend...")
    
    files = [
        ("files", (f"frame_{i}.jpg", f, "image/jpeg"))
        for i, f in enumerate(captured_images)
    ]

    try:
        # Increase timeout for batch processing
        res = requests.post(BACKEND_URL, files=files, timeout=60)
        res.raise_for_status()
        results = res.json().get("frames", [])
        status.success(f"✅ Received {len(results)} processed frames!")
    except Exception as e:
        status.error(f"❌ Backend connection failed: {e}")
        st.stop()

    # ---------- DISPLAY ----------
    st.divider()
    cols = st.columns(2)
    for i, img_b64 in enumerate(results):
        with cols[i % 2]:
            st.image(
                f"data:image/jpeg;base64,{img_b64}",
                caption=f"Result Frame {i+1}",
                use_container_width=True
            )