import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

from new_experiment import create_and_download
from utils import *

# Main function controlling the app workflow
def main():
    st.title("SRF: Database")
    options = ["Browse", "Create", "README"]
    selection = st.segmented_control("", options, selection_mode="single", default="Browse")

    if selection == "Browse":
        # Check login status; if not logged in, show login page
        if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
            if not login():
                return
                
        st.title("SRF: Query and Visualization")        
        st.write("Current working directory:", os.getcwd())

        experiments_df = load_experiments()

        # Filter experiments by processing tags ("recipes")
        if st.checkbox("Filter by *recepies*"):
            all_tags = get_all_processing_tags()
            selected_tags = st.pills("Processes applied in the history of the cavity", all_tags, selection_mode="multi")
            if selected_tags:
                st.success(f"Selected tags: {', '.join(selected_tags)}")
                matched_ids = set()
                for tag in selected_tags:
                    ids = get_experiments_by_processing_tag(tag)
                    matched_ids.update(ids)
                if matched_ids:
                    experiments_df = experiments_df[experiments_df['experiment_id'].isin(matched_ids)]
                else:
                    st.warning(f"No experiments found with selected tags: {', '.join(selected_tags)}")
            else:
                st.info("No tags selected.")

        display_experiments(experiments_df)

        # Filter experiments by metadata columns
        if st.checkbox("Filter by metadata information"):        
            filtered_experiments_df = filter_experiments(experiments_df)
        else:
            filtered_experiments_df = experiments_df

        if not filtered_experiments_df.empty:
            experiment_name = st.selectbox("Select Experiment", filtered_experiments_df['experiment_name'])
            experiment_id = filtered_experiments_df[filtered_experiments_df['experiment_name'] == experiment_name]['experiment_id'].iloc[0]

            # Show processing steps if available
            processing_df = load_processing_steps_for_experiment(experiment_id)
            if not processing_df.empty:
                if st.checkbox("Show Processing Steps Table"):
                    st.write("### Processing Steps")
                    selected_columns = ["process_type","description","temperature_c","duration_h","tags"]
                    st.dataframe(processing_df[selected_columns])
            else:
                st.info("No processing steps available for this experiment.")

            # Show raw data if available
            experiment_data_df = load_data_for_experiment(experiment_id)
            if not experiment_data_df.empty:
                if st.checkbox("Show Raw Data Table"):
                    st.write(f"### Data for Experiment: {experiment_name}")
                    selected_columns = st.multiselect("Select columns to display", experiment_data_df.columns.tolist(), default=experiment_data_df.columns.tolist(), key="raw")
                    st.dataframe(experiment_data_df[selected_columns])
            else:
                st.info("No raw data found for this experiment.")

            filtered_data_df = experiment_data_df

            # Optionally filter raw data
            if not experiment_data_df.empty:
                if st.checkbox("Filter the raw data"):
                    filtered_data_df = filter_data(experiment_data_df)
            else:
                st.info("No data available to filter.")

            # Plot data if available
            if not filtered_data_df.empty:
                if st.checkbox("Plot some data"):
                    plot_data(filtered_data_df)
            else:
                st.info("No data available to plot.")

            # Load and display associated png plots if available
            plots_df = load_plots_for_experiment(experiment_id)
            if not plots_df.empty:
                if st.checkbox("Load png plots"):
                    st.write("### Associated Plots")
                    for _, row in plots_df.iterrows():
                        if os.path.exists(row['file_path']):
                            st.image(row['file_path'], caption=row['caption'] if row['caption'] else "", use_container_width=True)
                        else:
                            st.warning(f"Image file not found: {row['file_path']}")
            else:
                st.info("No plots found for this experiment.")
    elif selection == "Create":
        create_and_download()

    elif selection == "README":
        # Leggi il contenuto del file README.md
        with open("README.md", "r", encoding="utf-8") as file:
            readme_content = file.read()

        # Mostra il contenuto con st.markdown (interpretando il Markdown)
        st.markdown(readme_content, unsafe_allow_html=True)

# Entry point
if __name__ == "__main__":
    main()     