import streamlit as st
import cv2
import numpy as np
from PIL import Image
import dropbox
import tempfile

st.title("Face Data Collection App")

# Dropbox
ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

st.write("Use your webcam to capture face images.")

# Webcam capture
cap = cv2.VideoCapture(0)

take_photo = st.button("Take Photo")
stop_capture = st.button("Stop")

if take_photo:
    ret, frame = cap.read()
    if ret:
        # تحويل BGR -> RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(img_rgb, caption="Captured Image", use_column_width=True)

        # حفظ مؤقت
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        Image.fromarray(img_rgb).save(temp_file.name)

        # رفع على Dropbox
        dropbox_path = f"/faces/{temp_file.name.split('/')[-1]}"
        with open(temp_file.name, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path)
        st.success(f"Photo saved to Dropbox: {dropbox_path}")

if stop_capture:
    cap.release()
    st.write("Camera stopped.")
