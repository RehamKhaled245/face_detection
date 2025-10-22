import streamlit as st
import cv2
import tempfile
import time
import dropbox
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode

# إعداد صفحة التطبيق
st.set_page_config(page_title="📸 Face Collector (Cloud)", layout="centered")

st.title("📸 Face Collector (Streamlit Cloud)")
st.markdown("""
### 🧠 How to use:
1. Enter your full name below.  
2. Click **Start Camera** to open your webcam.  
3. Position your face in front of the camera.  
4. Click **📸 Capture** to save the photo to Dropbox.
""")

# ---------- إعداد Dropbox ----------
ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def upload_to_dropbox(file_path, student_name, file_name):
    """رفع الصورة إلى مجلد Dropbox باسم الطالب"""
    dropbox_folder = f"/{student_name}"
    try:
        dbx.files_get_metadata(dropbox_folder)
    except dropbox.exceptions.ApiError:
        dbx.files_create_folder_v2(dropbox_folder)
    dropbox_path = f"{dropbox_folder}/{file_name}"
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    return dropbox_path


# ---------- مدخلات المستخدم ----------
student_name = st.text_input("📝 Enter student name:")
if "photo_count" not in st.session_state:
    st.session_state.photo_count = 0


# ---------- كلاس معالجة الفيديو ----------
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame = img
        return frame


# ---------- إعداد WebRTC (Cloud Friendly) ----------
webrtc_ctx = webrtc_streamer(
    key="reham-face-cloud",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    rtc_configuration={
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},  # سيرفر STUN من Google
        ]
    },
    async_processing=True,
)

# ---------- زر التقاط الصور ----------
if st.button("📸 Capture Photo"):
    if not student_name:
        st.error("⚠️ Please enter your name first!")
    elif not webrtc_ctx or not webrtc_ctx.video_processor or webrtc_ctx.video_processor.frame is None:
        st.error("⚠️ No frame detected! Make sure camera is started.")
    else:
        img = webrtc_ctx.video_processor.frame.copy()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            cv2.imwrite(tmp.name, img)
            file_name = f"{student_name}_{int(time.time())}.jpg"
            dropbox_path = upload_to_dropbox(tmp.name, student_name, file_name)
        st.session_state.photo_count += 1
        st.success(f"✅ Photo saved to Dropbox: {dropbox_path}")
        st.info(f"Total photos for {student_name}: {st.session_state.photo_count}")
