import streamlit as st
import cv2
import tempfile
import dropbox
import time
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

# ---------- Page Setup ----------
st.set_page_config(page_title="📸 Face Collector", layout="centered")

st.title("📸 Face Collector")
st.markdown("""
### How to use:
1. Enter your full name (First, Middle, Last).  
2. Click **Start Camera** to open webcam.  
3. Adjust your face in front of the camera.  
4. Click **Take Photo** to capture a single face image and save it to Dropbox.
""")

# ---------- Dropbox Setup ----------
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

# ---------- Inputs ----------
student_name = st.text_input("📝 Enter student name :")

# ---------- WebRTC Setup ----------
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

if "capturing" not in st.session_state:
    st.session_state.capturing = False
if "last_frame" not in st.session_state:
    st.session_state.last_frame = None
if "photo_count" not in st.session_state:
    st.session_state.photo_count = 0

class VideoCaptureTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        st.session_state.last_frame = img
        return img

# ---------- Buttons ----------
col1, col2 = st.columns([1,1])
with col1:
    if st.button("📷 Start Camera"):
        st.session_state.capturing = True
with col2:
    if st.button("📸 Take Photo"):
        if not student_name:
            st.error("⚠️ Please enter a student name first!")
        elif st.session_state.last_frame is None:
            st.error("⚠️ No frame available! Make sure the camera is started.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                cv2.imwrite(tmp.name, st.session_state.last_frame)
                file_name = f"{student_name}_{int(time.time())}.jpg"
                dropbox_path = upload_to_dropbox(tmp.name, student_name, file_name)
            st.session_state.photo_count += 1
            st.success(f"✅ Saved to Dropbox: {dropbox_path}")
            st.info(f"Total photos taken for {student_name}: {st.session_state.photo_count}")

# ---------- WebRTC Stream ----------
if st.session_state.capturing:
    webrtc_streamer(
        key="face-collector",
        video_processor_factory=VideoCaptureTransformer,
        rtc_configuration=RTC_CONFIGURATION
    )
