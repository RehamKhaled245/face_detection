import streamlit as st
import cv2
import time
import tempfile
import dropbox
from PIL import Image

# إعداد الصفحة
st.set_page_config(page_title="📸 Face Collector", layout="centered")

st.title("📸 Face Collector")
st.markdown("""
<div style="background-color:#000000;padding:20px;border-radius:10px;border:1px solid #ddd;">
<h3 style="color:#2c3e50;">📸 How to Use the App</h3>
<ol style="line-height:1.8;">
<li><b>Enter your full name</b> — First, Middle, and Last name.</li>
<li>Click <b>Take a Photo</b> to capture and save your image.</li>
<li>Your image will be <b>automatically uploaded</b> to Dropbox.</li>
<li>To retake, click <b>Clear Photo</b> and then <b>Take a Photo</b> again.</li>
</ol>
</div>
""", unsafe_allow_html=True)


# ---------- إعداد Dropbox ----------
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

# ---------- إدخال الاسم ----------
student_name = st.text_input("📝 Enter student name:")

# ---------- التقاط الصورة ----------
camera_image = st.camera_input("📷 Take a photo")

if camera_image is not None and student_name:
    # حفظ الصورة مؤقتاً
    img = Image.open(camera_image)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        img.save(tmp.name)
        file_name = f"{student_name}_{int(time.time())}.jpg"
        dropbox_path = upload_to_dropbox(tmp.name, student_name, file_name)

    st.success(f"✅ Photo saved to Dropbox: {dropbox_path}")
    st.image(img, caption="Captured Image", use_container_width=True)

elif camera_image is not None and not student_name:
    st.warning("⚠️ Please enter your name before taking a photo!")



