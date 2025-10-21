import streamlit as st
import cv2
import tempfile
import dropbox
import time

st.set_page_config(page_title="📸 Face Collector (Take Photo + Dropbox)", layout="centered")

st.title("📸 Face Collector")
st.markdown("""
### How to use:
1. Enter your full name (First, Middle, Last).  
2. Click **Open Camera** to start the webcam.
3. Adjust your face in front of the camera.
4. Click **Take Photo** to capture a single face image and save it to Dropbox.
""")

# ---------- Dropbox setup ----------
ACCESS_TOKEN = "sl.u.AGAfuWRAOt0Ing4F4tBfY3aHE7bXlZnXw0wPk9aIfrV8pGg-c1suQu2WOshdCHDWoafdi-zzAXman8BFxARVIQETRZ5w77G6dPoY0SPLSTpHD7PjJz1zlxxVfXFP14eYL90UpM38WplIaAz0EIoV0YNvJSCncpuULiDd3gW9d0TVl0lFYwCHnq_4WOQedNfNqXZpYN4mI6PatW7cQMvX1NbkcXKmzseJ-jXF6aN6YJwKxOlIahj6bNJqBG9uMYD0HDc29Lz37_puew0ZrXntxLJH68dlnDiwTc7stB8gRgNV_OBvyRGbg7oGbTVTmcSA7aB7SpYMCRdYxaA9IzuM4s4ZhP2AGU5n2tgIK-G8dSZllEFH21XRCHpdEH8zejZbOIP9M2HILcgyS3DUBEzjUH8zs8qxEqSX63qL3H0VfXHxdhQkGeSV5pI9K50p-WnydU3mRxMa9fz-kgv1UvQcLJ7JF7575IMNp2jaQ0VGgAZaOdts1eiZF4NHYaxiIfo2u8em9-y0ZCJS-LNclXqvAH5J8XRzkVlB2BLesWRxgiFfdlLhDoGEmuAplLdQX5vD_imZFiPZhCxQnld6azYn4j45hj5RlNQTqZsZIAtnTaedxHky6ji7XORKr15H5vz4lufkNTd49lDRrS20FnZwnYMM_DkBnUsmFEmvFGagsURSDZyB7AzNHPOUmIBSDlwapfkMOyptzgETsswJTfF-Ihf6-C3xMoug7zrYi1VeNyGIVjDwdXHKFnT-0-a6RIiipe8puVTDS3mYtMtgGDPr53QL-dkzhHXRw2L2NB6-89E9jfrPKloPjaHRIofoafd0kLmM3vyti9gvbkiMma-ASnrNwULDCMH4twxX_T3cQJz-prFuJbqAZ_QJNkfFF_QWeW9335FbPkNWGYQbzmVmkvItjYgfA2YHa9xnmpReVI-7uYC6DQDdJvnaMH9NHhPns-8PnhXrpd8D-2u0IwIBhcHFGh1OfxMgKuYDjB-e_jxXY4knfOqJ-8RsyCE3CA2ZgA1ZbvTR39o5ErQ6dBsz-zsUneikSKxnSFsK9RF2XtH9N6XQvd8FMEfpC4QRDrSdfmtrJCKWD-TLV3os3eS8TIzhTuWVZLhPwjU-Y1jgQCxa3D2_PqVq8Em2HTnUPE_0EwEAbFfn2UJ0X_pFbOsY7l-CEeIWxSSXKG6cdwgMsRGwPBYA01imlCUStXAjJsm3q-9nheH0ZO_z86lnOmaYEk5ELLJyuauAfagWIXUpgQs3OKBxMtLdPYmtALLaVm2bNZhm48L0oJ44A08cb5QV46tNxxibWcQc3XHID0K5--vtXtjbSVDggPfJ2i1_d_7VfvTShUg1cS6LMdwihkXMfY2jFWUA_mLCNYJdvwCCL9iweomvYHTniNiYsn6EzhzijxUgOfBB9F58YHCxY8y3YSTSiJCga-UNLWmWLHlaz_F2wg"
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

# ---------- Streamlit Inputs ----------
student_name = st.text_input("📝 Enter student name :")

open_cam = st.button("📷 Open Camera")
frame_placeholder = st.empty()

# ---------- Session State ----------
if "cap" not in st.session_state:
    st.session_state.cap = None
if "photo_count" not in st.session_state:
    st.session_state.photo_count = 0

# ---------- Start webcam ----------
if open_cam:
    st.session_state.cap = cv2.VideoCapture(0)
    st.success("✅ Camera opened! Adjust your face and click Take Photo.")

if st.session_state.cap:
    ret, frame = st.session_state.cap.read()
    if ret:
        st.markdown("**👀 Adjust your face in the frame before taking the photo.**")
        frame_placeholder.image(frame, channels="BGR")
    else:
        st.error("⚠️ Cannot access webcam!")

# ---------- Take Photo Button ----------
if st.button("📸 Take Photo"):
    if not student_name:
        st.error("⚠️ Please enter a student name first!")
    elif st.session_state.cap is None:
        st.error("⚠️ Open the camera first!")
    else:
        ret, frame = st.session_state.cap.read()
        if ret:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                cv2.imwrite(tmp.name, frame)
                file_name = f"{student_name}_{int(time.time())}.jpg"
                dropbox_path = upload_to_dropbox(tmp.name, student_name, file_name)
            st.session_state.photo_count += 1
            st.success(f"✅ Saved to Dropbox: {dropbox_path}")
            st.info(f"Total photos taken for {student_name}: {st.session_state.photo_count}")
        else:
            st.error("❌ Failed to capture image.")
