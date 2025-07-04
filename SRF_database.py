# SRF_database.py
# Streamlit UI to browse the SRF database, add new data, and display the README

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Import the main page modules for different app functionalities
from utils.browser import browser_page                  # Page to browse and visualize the database
from utils.new_experiment import new_experiment_page    # Page to create and upload new experiments
from utils.utils import *                               # Utility functions used across pages

def main():
    """
    Main function controlling the overall app workflow and navigation.
    Provides a segmented control UI to switch between:
    - Browse: View and query existing database entries
    - Create: Add new experimental data to the database
    - README: Show the README documentation with instructions and info
    """
    LOGO_LASA = "utils/images/logo_bloom.png"
    LASA_LINK = "https://homelasa.mi.infn.it/en/"
    st.logo(LOGO_LASA, icon_image=LOGO_LASA, link=LASA_LINK)
    with open("utils/streamlit_README.md", "r", encoding="utf-8") as file:
        readme_content = file.read()
    st.sidebar.markdown(readme_content, unsafe_allow_html=True)
    # st.title("SRF: Database")
    st.header("SRF: Database", divider=True)

    # Navigation control allowing user to switch between modes/pages
    options = ["Browse", "Create", "README"]
    selection = st.segmented_control(
        "Navigation",
        options,
        selection_mode="single",
        default="Browse"
    )

    # Route to the corresponding page based on user selection
    if selection == "Browse":
        browser_page()

    elif selection == "Create":
        new_experiment_page()

    elif selection == "README":
        # Read and display the README markdown file with instructions/documentation
        with open("utils/streamlit_README.md", "r", encoding="utf-8") as file:
            readme_content = file.read()

        st.markdown(readme_content, unsafe_allow_html=True)

# Standard Python entry point guard
if __name__ == "__main__":
    main()