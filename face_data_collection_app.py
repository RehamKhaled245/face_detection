import streamlit as st
from streamlit_camera_input import camera_input
import cv2
import numpy as np
import tempfile
import dropbox
import time

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

# ---------- Streamlit UI ----------
st.set_page_config(page_title="📸 Face Collector", layout="centered")
st.title("📸 Face Collector")

st.markdown("""
### How to use:
1. Enter your full name (First, Middle, Last).  
2. Click **Open Camera** to take a photo from your browser.  
3. Adjust your face in front of the camera.  
4. The photo will be saved automatically to Dropbox.
""")

student_name = st.text_input("📝 Enter student name :")

# ---------- Camera Input ----------
img_file_buffer = camera_input("📷 Open Camera")

if img_file_buffer is not None:
    if not student_name:
        st.error("⚠️ Please enter a student name first!")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img_file_buffer.getbuffer())
            file_name = f"{student_name}_{int(time.time())}.jpg"
            dropbox_path = upload_to_dropbox(tmp.name, student_name, file_name)
        st.success(f"✅ Saved to Dropbox: {dropbox_path}")
