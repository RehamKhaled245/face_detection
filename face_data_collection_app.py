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
### How to use:
1. Enter your full name (First, Middle, Last).  
2. Click **Take a Photo** to Save photo.  
3.Your image will be uploaded to Dropbox automatically.
4.Click **Clear Photo**  and Click **Take a Photo** to take another photo.
""")

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

