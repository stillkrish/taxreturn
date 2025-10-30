import streamlit as st
from PIL import Image
import json
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="1040 Field Mapper", layout="wide")
st.title("🗺️ Form 1040 Coordinate Mapper")

st.caption(
    "Click on each field you want to label. "
    "The coordinates (in ReportLab's coordinate system) will be saved to a JSON mapping."
)

uploaded = st.file_uploader("Upload a page image (PNG)", type=["png", "jpg"])

if uploaded:
    img = Image.open(uploaded)
    width, height = img.size
    st.image(img, caption=f"Image size: {width}×{height}", width=850)
    coords = streamlit_image_coordinates(img, key="mapper", width=850)


    # --- Session state for mapping ---
    if "field_map" not in st.session_state:
        st.session_state.field_map = {}

    if coords is not None:
        x = round(coords["x"], 2)
        y = round(height - coords["y"], 2)  # convert to bottom-left origin
        field_label = st.text_input("Enter field label (e.g. line1a_wages, line2b_interest):", key=f"label_{x}_{y}")
        if st.button("Add Field", key=f"btn_{x}_{y}"):
            st.session_state.field_map[field_label] = {"x": x, "y": y}
            st.success(f"✅ Added {field_label} → ({x}, {y})")

    if st.session_state.field_map:
        st.subheader("📋 Current field map")
        st.json(st.session_state.field_map)

        # Export option
        if st.button("💾 Export JSON"):
            json_str = json.dumps(st.session_state.field_map, indent=2)
            st.download_button(
                "⬇️ Download field_map_1040.json",
                data=json_str,
                file_name="field_map_1040.json",
                mime="application/json",
            )
else:
    st.info("📤 Upload your flattened 1040 image (e.g. f1040_page1.png) to begin.")
