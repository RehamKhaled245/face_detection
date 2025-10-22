import streamlit as st
import cv2
import tempfile
import time
import dropbox
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# ---------- Page Setup ----------
st.set_page_config(page_title="📸 Face Collector", layout="centered")

st.title("📸 Face Collector")
st.markdown("""
### How to use:
1. Enter your full name (First, Middle, Last).  
2. Click **Start Camera** to open webcam from your browser.  
3. Adjust your face in front of the camera.  
4. Click **Take Photo** to capture a single face image and save it to Dropbox.
""")

# ---------- Dropbox setup ----------
ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def upload_to_dropbox(file_path, student_name, file_name):
    dropbox_folder = f"/{student_name}"
    try:
        dbx.files_get_metadata(dropbox_folder)
    except dropbox.exceptions.ApiError:
        dbx.files_create_folder_v2(dropbox_folder)
    dropbox_path = f"{dropbox_folder}/{file_name}"
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    return dropbox_path

# ---------- User Input ----------
student_name = st.text_input("📝 Enter student name:")

if "photo_count" not in st.session_state:
    st.session_state.photo_count = 0
if "capturing" not in st.session_state:
    st.session_state.capturing = False

# ---------- Video Processor ----------
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame = img
        return frame

# ---------- Buttons ----------
col1, col2 = st.columns([1, 1])

with col1:
    start_camera = st.button("▶️ Start Camera")
with col2:
    stop_camera = st.button("⏹ Stop Camera")

if start_camera:
    st.session_state.capturing = True
if stop_camera:
    st.session_state.capturing = False

# ---------- WebRTC with STUN config ----------
if st.session_state.capturing:
      webrtc_ctx = webrtc_streamer(
        key="face",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
        rtc_configuration={
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {
                    "urls": ["turn:relay.metered.ca:80", "turn:relay.metered.ca:443"],
                    "username": "openai",
                    "credential": "openai"
                }
            ]
        }
    )


    # ---------- Capture & Upload ----------
    if st.button("📸 Take Photo"):
        if not student_name:
            st.error("⚠️ Please enter a student name first!")
        elif webrtc_ctx.video_processor is None or webrtc_ctx.video_processor.frame is None:
            st.error("⚠️ No frame available! Make sure the camera is started.")
        else:
            img = webrtc_ctx.video_processor.frame.copy()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                cv2.imwrite(tmp.name, img)
                file_name = f"{student_name}_{int(time.time())}.jpg"
                dropbox_path = upload_to_dropbox(tmp.name, student_name, file_name)

            st.session_state.photo_count += 1
            st.success(f"✅ Saved to Dropbox: {dropbox_path}")
            st.info(f"📷 Total photos taken for {student_name}: {st.session_state.photo_count}")


