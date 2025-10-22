import streamlit as st
from PIL import Image
import dropbox

st.title("Face Data Collection App (Online Upload)")

ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

uploaded_file = st.file_uploader("Upload an image of your face", type=["jpg", "png"])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # رفع على Dropbox
    dropbox_path = f"/faces/{uploaded_file.name}"
    dbx.files_upload(uploaded_file.getvalue(), dropbox_path)
    st.success(f"Photo saved to Dropbox: {dropbox_path}")
