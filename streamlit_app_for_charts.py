import streamlit as st
import os
import json
import pandas as pd
from PIL import Image
from pathlib import Path
import base64
from xml.etree import ElementTree as ET

# Define the SVG namespace
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NAMESPACE)  # Register the SVG namespace

# --- Configurations ---
ROOT = Path("/Users/vanshikamk/Desktop/Document_Layout")
image_folder = ROOT / "input_data/EvalSamplesCharts/BenetechRasters"
FT_svg_folder = ROOT / "results/Charts_FT/BenetechRasters/svg"
FT_json_folder = ROOT / "results/Charts_FT/BenetechRasters"
Gemini_svg_folder = ROOT / "results/Charts_Gemini/BenetechCharts/svg"
Gemini_json_folder = ROOT / "results/Charts_Gemini/BenetechCharts"
comments_file = "ChartsEvaluationResults.csv"

# --- Load image filenames ---
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png') or f.endswith('.jpg')])

# --- UI ---
st.set_page_config(layout="wide", page_title="Charts Evaluation")
st.title("Chart Comparison Tool")

if "index" not in st.session_state:
    st.session_state.index = 0

# Function to load SVG files and convert them to a format viewable in Streamlit
def load_svg(file_path):
    with open(file_path, "r") as svg_file:
        svg_content = svg_file.read()
    b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    # svg_display = f'<img src="data:image/svg+xml;base64,{b64_svg}" />'
    # Add CSS for fixed height and centering
    svg_display = f"""
    <div style="
        height: 500px; 
        display: flex; 
        justify-content: center; 
        align-items: center;
        background-color: #f8f8f8; 
    ">
        <img src="data:image/svg+xml;base64,{b64_svg}" style="max-height: 100%; width: auto;" />
    </div>
    """
    return svg_display

if image_files:
    # Navigation Buttons
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("⬅️ Previous") and st.session_state.index > 0:
            st.session_state.index -= 1
    with col_next:
        if st.button("Next ➡️") and st.session_state.index < len(image_files) - 1:
            st.session_state.index += 1

    selected_image = image_files[st.session_state.index]
    base_name = Path(selected_image).stem

    image_path = image_folder / selected_image
    FT_svg_path = FT_svg_folder / f"output_{base_name}.svg"
    FT_json_path = FT_json_folder / f"{base_name}.json"
    Gemini_svg_path = Gemini_svg_folder / f"output_{base_name}.svg"
    Gemini_json_path = Gemini_json_folder / f"{base_name}.json"

    # Layout
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Original PNG")
        st.image(Image.open(image_path), use_container_width=True)

    with col2:
        st.subheader("FT SVG")
        if FT_svg_path.exists():
            st.markdown(load_svg(FT_svg_path), unsafe_allow_html=True)
            # with open(FT_svg_path, "r", encoding="utf-8") as f:
                # st.components.v1.html(f.read(), height=300, scrolling=True)
        else:
            st.warning("FT SVG not found.")

        st.subheader("FT JSON")
        if FT_json_path.exists():
            with open(FT_json_path, "r", encoding="utf-8") as f:
                st.json(json.load(f))
        else:
            st.warning("FT JSON not found.")
    
    with col3:
        st.subheader("Gemini SVG")
        if Gemini_svg_path.exists():
            st.markdown(load_svg(Gemini_svg_path), unsafe_allow_html=True)
            # with open(Gemini_svg_path, "r", encoding="utf-8") as f:
            #     st.components.v1.html(f.read(), height=300, scrolling=True)
        else:
            st.warning("Gemini SVG not found.")

        st.subheader("Gemini JSON")
        if Gemini_json_path.exists():
            with open(Gemini_json_path, "r", encoding="utf-8") as f:
                st.json(json.load(f))
        else:
            st.warning("Gemini JSON not found.")

    # Comments section
    st.markdown("---")
    st.subheader("Comments")
    comment = st.text_area("Add your comment about the accuracy of the chart or any observation", key=base_name)

    if st.button("Save Comment"):
        new_entry = {
            "image": selected_image,
            "comment": comment
        }
        # Save to CSV
        if os.path.exists(comments_file):
            df = pd.read_csv(comments_file)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])
        df.to_csv(comments_file, index=False)
        st.success("Comment saved!")
else:
    st.warning("No PNG images found.")
