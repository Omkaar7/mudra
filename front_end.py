import streamlit as st
import streamlit.components.v1 as components
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="YOLOv11 Realtime", layout="wide")
st.title("🎥 YOLOv11 Real-Time Detection")

if "run" not in st.session_state:
    st.session_state.run = False

col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Start Webcam"):
        requests.post(f"{API}/start")
        st.session_state.run = True

with col2:
    if st.button("⏹ Stop Webcam"):
        requests.post(f"{API}/stop")
        st.session_state.run = False

if st.session_state.run:
    components.html(
        f"""
        <div style="display:flex;justify-content:center;">
            <img src="{API}/video_feed" style="max-height:65vh;" />
        </div>
        """,
        height=480,
    )
else:
    st.success("Camera stopped — LED should be OFF")
