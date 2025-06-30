# new_experiment.py
# streamlit interface to create and download a zip with a new experiment
import streamlit as st
import io
import json
import zipfile
from datetime import datetime

# --- Generic Helper Functions for List Management ---
def move_item_up(list_name, index):
    items = st.session_state[list_name]
    if index > 0:
        items[index - 1], items[index] = items[index], items[index - 1]
    st.session_state[list_name] = items

def move_item_down(list_name, index):
    items = st.session_state[list_name]
    if index < len(items) - 1:
        items[index + 1], items[index] = items[index], items[index + 1]
    st.session_state[list_name] = items

def remove_item(list_name, index):
    items = st.session_state[list_name]
    items.pop(index)
    st.session_state[list_name] = items

def insert_item_after(list_name, index, default_item):
    items = st.session_state[list_name]
    items.insert(index + 1, default_item)
    st.session_state[list_name] = items

def append_item(list_name, default_item):
    st.session_state[list_name].append(default_item)

# --- Load processes from JSON ---
@st.cache_data
def load_processes():
    with open("utils/processes.json", "r", encoding="utf-8") as f:
        return json.load(f)

processes = load_processes()

# Prepare default step tag for "Else"
default_tags = processes["Else"].get("tags", [])
default_tag = default_tags[0] if default_tags else None
default_step = {
    "process_type": "",
    "description": "",
    "tag": default_tag,
    **{k: 0.0 for k in processes["Else"]["parameters"]}
}

# --- Main App ---
def create_and_download():
    st.title("Add new Data Set")

    col1, col2 = st.columns(2)
    with col1:
        experiment_name = st.text_input("Experiment Name", value="FNAL_103.1")
        date = st.date_input("Date", value=datetime.strptime("2025-01-28", "%Y-%m-%d"))
    with col2:
        lab_name = st.text_input("Lab Name", value="FNAL")
        article_url = st.text_input("Article URL", value="https://arxiv.org/abs/2401.12345")
    description = st.text_area("Description", value="Lore lipsium (data)")

    # --- Processing Steps ---
    if "proc_enabled" not in st.session_state:
        st.session_state.proc_enabled = False
    if "proc_steps" not in st.session_state:
        st.session_state.proc_steps = []

    proc_enabled = st.checkbox("Define processing steps", key="proc_enabled")

    if proc_enabled:
        for i, step in enumerate(st.session_state.proc_steps):
            with st.expander(f"Processing Step {i+1}", expanded=True):

                st.markdown("**Select Process Type**")
                cols = st.columns(len(processes))
                current_type = step.get("process_type", "")

                # Process type pills/buttons (single select)
                for idx, proc_name in enumerate(processes.keys()):
                    btn_label = proc_name
                    if cols[idx].button(btn_label, key=f"ptype_btn_{i}_{proc_name}"):
                        step["process_type"] = proc_name
                        # Select first tag of this process by default, or None if no tags
                        tags_list = processes[proc_name].get("tags", [])
                        step["tag"] = tags_list[0] if tags_list else None
                        # Initialize parameters from JSON defaults
                        for param in processes[proc_name]["parameters"]:
                            step[param] = processes[proc_name]["parameters"][param]

                selected_type = step.get("process_type", "")
                if selected_type:
                    st.markdown(f"**Selected Process Type:** `{selected_type}`")
                else:
                    st.markdown("*No process type selected yet*")

                # --- Tag Selection (Single Tag as Pills) ---
                all_tags = processes.get(selected_type, {}).get("tags", [])
                if "tag" not in step:
                    step["tag"] = None

                st.markdown("**Select One Tag**")
                tag_cols = st.columns(max(1, len(all_tags)))
                for j, tag in enumerate(all_tags):
                    tag_label = tag
                    if tag_cols[j].button(tag_label, key=f"tag_{i}_{j}"):
                        if step["tag"] == tag:
                            step["tag"] = None  # Deselect if clicked again
                        else:
                            step["tag"] = tag

                st.markdown(f"**Selected Tag:** `{step['tag']}`")

                # --- Parameters ---
                st.markdown("**Parameters**")
                for param_name in processes.get(selected_type, {}).get("parameters", {}):
                    default_val = step.get(param_name, 0.0)
                    step[param_name] = st.number_input(
                        f"{param_name}",
                        value=default_val,
                        key=f"param_{i}_{param_name}",
                        format="%.2f"
                    )

                # Description text input
                step['description'] = st.text_input(
                    f"Description {i+1}",
                    value=step.get("description", ""),
                    key=f"desc_{i}"
                )

                # --- Controls to reorder / remove / add steps ---
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.button(f"⬆️ Move Up {i+1}", key=f"up_step_{i}", on_click=move_item_up, args=("proc_steps", i))
                with col2:
                    st.button(f"⬇️ Move Down {i+1}", key=f"down_step_{i}", on_click=move_item_down, args=("proc_steps", i))
                with col3:
                    st.button(f"❌ Remove Step {i+1}", key=f"remove_step_{i}", on_click=remove_item, args=("proc_steps", i))
                with col4:
                    st.button(f"➕ Add Step After {i+1}", key=f"add_after_step_{i}", on_click=insert_item_after,
                              args=("proc_steps", i, default_step))

        st.button("➕ Add Step", on_click=append_item, args=("proc_steps", default_step))

    # --- Raw Data ---
    if "raw_data_enabled" not in st.session_state:
        st.session_state.raw_data_enabled = False
    if "raw_data_text" not in st.session_state:
        st.session_state.raw_data_text = """Time\tTemp_Diode\tMKS1000\tLowerEdge\tBandwidth\tCenter_Stimulus\tQualityFactor\tLowerEdge\tLoss\tMax_Freq
3820892610.073\t293.640\t986.690\t648833686.000\t55326.000\t648861348.410\t11727.964\t648889012.000\t76.549\t648861348.410
3820892612.590\t293.614\t986.990\t648833686.000\t55326.000\t648861348.410\t11727.964\t648889012.000\t76.549\t648861348.410"""

    raw_data_enabled = st.checkbox("Include Raw Data", key="raw_data_enabled")

    raw_data_text = ""
    filename_base = experiment_name.replace(" ", "_")

    if raw_data_enabled:
        filename_base = st.text_input("Base filename (without extension)", value=filename_base)
        raw_data_text = st.text_area("Raw data text", height=200, value=st.session_state.raw_data_text, key="raw_text_area")

    # --- Images ---
    if "images_enabled" not in st.session_state:
        st.session_state.images_enabled = False
    if "image_files" not in st.session_state:
        st.session_state.image_files = []

    images_enabled = st.checkbox("Attach images (PNG/JPEG)", key="images_enabled")

    if images_enabled:
        for i in range(len(st.session_state.image_files)):
            with st.expander(f"Image {i+1}", expanded=True):
                uploaded_file = st.file_uploader(
                    f"Upload Image {i+1}", type=["png", "jpg", "jpeg"], key=f"image_upload_{i}"
                )
                if uploaded_file is not None:
                    st.session_state.image_files[i] = uploaded_file
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.button(f"⬆️ Move Up Image {i+1}", key=f"img_up_{i}", on_click=move_item_up, args=("image_files", i))
                with col2:
                    st.button(f"⬇️ Move Down Image {i+1}", key=f"img_down_{i}", on_click=move_item_down, args=("image_files", i))
                with col3:
                    st.button(f"❌ Remove Image {i+1}", key=f"img_remove_{i}", on_click=remove_item, args=("image_files", i))
                with col4:
                    st.button(f"➕ Add Image After {i+1}", key=f"img_add_after_{i}", on_click=insert_item_after, args=("image_files", i, None))

        st.button("➕ Add Another Image", on_click=append_item, args=("image_files", None))

    # --- Generate and Download ZIP ---
    if st.button("Generate and Download Data ZIP"):
        if not filename_base:
            st.error("Please enter a base filename.")
            return
        if raw_data_enabled and not raw_data_text.strip():
            st.error("Raw data text cannot be empty.")
            return

        metadata = {
            "experiment_name": experiment_name,
            "lab_name": lab_name,
            "description": description,
            "date": date.strftime("%Y-%m-%d"),
            "article_url": article_url,
            "processing_steps": []
        }

        if proc_enabled:
            for step in st.session_state.proc_steps:
                cleaned_step = {
                    k: (v if v not in [None, 0, 0.0, "", []] else None)
                    for k, v in step.items()
                }
                cleaned_step = {k: v for k, v in cleaned_step.items() if v is not None}
                metadata["processing_steps"].append(cleaned_step)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("metadata.json", json.dumps(metadata, indent=2))
            if raw_data_enabled:
                zf.writestr(f"{filename_base}_data.txt", raw_data_text)
            if images_enabled:
                for idx, img_file in enumerate(st.session_state.image_files):
                    if img_file is not None:
                        ext = img_file.name.split('.')[-1]
                        zf.writestr(f"{filename_base}_image_{idx+1}.{ext}", img_file.getbuffer())

        zip_buffer.seek(0)
        st.success("ZIP file generated successfully!")
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name=f"{filename_base}.zip",
            mime="application/zip"
        )