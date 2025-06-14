import streamlit as st
import io
import json
import zipfile
from datetime import datetime

def create_and_download():
    st.title("Create and Download New Data Set")

    # Input metadata
    experiment_name = st.text_input("Experiment Name", value="FNAL_103.1")
    lab_name = st.text_input("Lab Name", value="FNAL")
    description = st.text_area("Description", value="Lore lipsium (data)")
    date = st.date_input("Date", value=datetime.strptime("2025-01-28", "%Y-%m-%d"))
    article_url = st.text_input("Article URL", value="https://arxiv.org/abs/2401.12345")

    st.write("### Processing Steps")

    # We'll let user add multiple processing steps
    # We'll keep the processing steps in session state for dynamic add/remove (simple version: fixed 3 steps)
    if "proc_steps" not in st.session_state:
        st.session_state.proc_steps = [
            {"process_type": "EP", "description": "EP 120um", "temperature C": None, "duration h": None, "tags": "EP"},
            {"process_type": "baking", "description": "baking 75C for 3h", "temperature C": 75, "duration h": 3, "tags": "lowT"},
            {"process_type": "BCP", "description": "BCP 20um", "temperature C": None, "duration h": None, "tags": "BCP"},
        ]

    proc_steps = st.session_state.proc_steps

    for i, step in enumerate(proc_steps):
        st.write(f"Processing Step {i+1}")
        step['process_type'] = st.text_input(f"Process Type {i+1}", value=step.get("process_type", ""), key=f"ptype_{i}")
        step['description'] = st.text_input(f"Description {i+1}", value=step.get("description", ""), key=f"desc_{i}")
        # Optional temperature and duration (only for some steps)
        step['temperature C'] = st.number_input(f"Temperature C {i+1} (optional)", value=step.get("temperature C") or 0.0, key=f"temp_{i}", format="%.2f")
        step['duration h'] = st.number_input(f"Duration h {i+1} (optional)", value=step.get("duration h") or 0.0, key=f"dur_{i}", format="%.2f")
        step['tags'] = st.text_input(f"Tags {i+1}", value=step.get("tags", ""), key=f"tags_{i}")

    # Raw data input (multiline text area)
    st.write("### Paste Raw Data (tab-delimited)")
    raw_data_text = st.text_area("Raw data text (e.g. tab separated columns)", height=200, value=
"""Time\tTemp_Diode\tMKS1000\tLowerEdge\tBandwidth\tCenter_Stimulus\tQualityFactor\tLowerEdge\tLoss\tMax_Freq
3820892610.073\t293.640\t986.690\t648833686.000\t55326.000\t648861348.410\t11727.964\t648889012.000\t76.549\t648861348.410
3820892612.590\t293.614\t986.990\t648833686.000\t55326.000\t648861348.410\t11727.964\t648889012.000\t76.549\t648861348.410
3820892615.058\t293.614\t987.502\t648833686.000\t55326.000\t648861348.410\t11727.964\t648889012.000\t76.549\t648861348.410
3820892616.039\t293.614\t987.668\t648833686.000\t55326.000\t648861348.410\t11727.964\t648889012.000\t76.549\t648861348.410
3820892618.341\t293.641\t988.052\t648830782.000\t58494.000\t648860028.341\t11092.762\t648889276.000\t76.724\t648860028.341
3820892618.896\t293.641\t988.211\t648830782.000\t57484.000\t648859523.363\t11287.654\t648888266.000\t76.724\t648859523.363
3820892622.364\t293.651\t988.525\t648830782.000\t57484.000\t648859523.363\t11287.654\t648888266.000\t76.724\t648859523.363
3820892676.879\t293.624\t986.280\t648831469.000\t58853.000\t648860894.833\t11025.112\t648890322.000\t76.782\t648860894.833"""
    )

    # Filename input
    filename_base = st.text_input("Base filename (without extension)", value=experiment_name.replace(" ", "_"))

    if st.button("Generate and Download Data ZIP"):
        if not filename_base:
            st.error("Please enter a base filename.")
            return
        if not raw_data_text.strip():
            st.error("Raw data text cannot be empty.")
            return

        # Compose metadata dictionary
        metadata = {
            "experiment_name": experiment_name,
            "lab_name": lab_name,
            "description": description,
            "date": date.strftime("%Y-%m-%d"),
            "article_url": article_url,
            "processing_steps": []
        }

        for step in proc_steps:
            # Clean step dict - remove keys with None or 0 values
            cleaned_step = {
                k: (v if v not in [None, 0, 0.0, ""] else None)
                for k, v in step.items()
            }
            # Remove keys with None values
            cleaned_step = {k: v for k, v in cleaned_step.items() if v is not None}
            metadata["processing_steps"].append(cleaned_step)

        # Create in-memory zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Add metadata.json
            zf.writestr(f"{filename_base}_metadata.json", json.dumps(metadata, indent=2))
            # Add raw data txt
            zf.writestr(f"{filename_base}_data.txt", raw_data_text)

        zip_buffer.seek(0)

        st.success("ZIP file generated successfully!")
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name=f"{filename_base}.zip",
            mime="application/zip"
        )