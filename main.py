import streamlit as st
import cv2
import tempfile
import numpy as np
from ultralytics import YOLO
from PIL import Image

# --- Page Config ---
st.set_page_config(
    page_title="PPE Detection App",
    page_icon="👷",
    layout="wide"
)

# --- Sidebar for Settings ---
st.sidebar.header("Model Settings")
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.50, 0.05)


# --- Load Model ---
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)


try:
    model = load_model("best.pt")
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# --- Main App Layout ---
st.title("👷 PPE Detection: Image & Video")
st.write("Upload an Image or Video to detect Personal Protective Equipment.")

# --- File Uploader ---
# Accepts mp4, avi, mov for video AND jpg, png, jpeg for images
uploaded_file = st.file_uploader("Choose a file...", type=["mp4", "avi", "mov", "jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Check file type based on extension
    file_type = uploaded_file.name.split('.')[-1].lower()

    # === IMAGE HANDLING ===
    if file_type in ['jpg', 'png', 'jpeg']:
        st.subheader("Results on Image")

        # Open and process image
        image = Image.open(uploaded_file)

        # Predict
        results = model.predict(image, conf=conf_threshold)

        # Plot results
        res_plotted = results[0].plot()

        # Display
        st.image(res_plotted, caption="Processed Image", use_column_width=True)

    # === VIDEO HANDLING ===
    elif file_type in ['mp4', 'avi', 'mov', 'mkv']:
        st.subheader("Results on Video")

        # Save temp video file
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        vf = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        while vf.isOpened():
            ret, frame = vf.read()
            if not ret:
                break

            # Predict
            results = model.predict(frame, conf=conf_threshold, verbose=False)
            res_plotted = results[0].plot()

            # Convert BGR to RGB for Streamlit
            frame_rgb = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
            stframe.image(frame_rgb, use_column_width=True)

        vf.release()