# utils.py
# additional functions for the streamlit interafe to query and plot the SRF database

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Define simple user credentials
USER_CREDENTIALS = {
    "lasa": "2025"
}

def get_db_connection():
    return sqlite3.connect(os.path.join("data", "srf_database.db"))

# Function to handle user login
def login():
    st.title("SRF: Login Page")

    if st.session_state.get("logged_in", False):
        st.success("Login Successful!")
        return True

    # Render the login form
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.session_state["logged_in"] = False
                st.error("Incorrect Username or Password")

    return False

# Load experiments metadata from the database
def load_experiments():
    conn = get_db_connection()
    query = "SELECT * FROM experiments"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load data for a specific experiment
def load_data_for_experiment(experiment_id):
    conn = get_db_connection()
    query = f"SELECT * FROM data WHERE experiment_id = {experiment_id}"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Pivot to restore wide format
    df_pivoted = df.pivot(index='row_index', columns='column_name', values='value')
    df_pivoted.reset_index(drop=True, inplace=True)
    return df_pivoted

# Load plots for a specific experiment
def load_plots_for_experiment(experiment_id):
    conn = get_db_connection()
    query = f"SELECT * FROM plots WHERE experiment_id = {experiment_id}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load processing steps for a specific experiment, ordered by step index
def load_processing_steps_for_experiment(experiment_id):
    conn = get_db_connection()
    query = f"SELECT * FROM processing_steps WHERE experiment_id = {experiment_id} ORDER BY step_index ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Get experiment IDs where processing steps contain a specific tag
def get_experiments_by_processing_tag(tag):
    conn = get_db_connection()
    query = """
        SELECT DISTINCT experiment_id
        FROM processing_steps
        WHERE tags LIKE ?
    """
    df = pd.read_sql(query, conn, params=(f"%{tag}%",))
    conn.close()
    return df['experiment_id'].tolist()

# Get all distinct processing tags from the processing_steps table
def get_all_processing_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tags FROM processing_steps")
    rows = cursor.fetchall()
    conn.close()
    # Filter out None or empty tags and sort
    return sorted(tag[0] for tag in rows if tag[0])

# Display the experiments metadata dataframe
def display_experiments(df):
    st.write("### Experiments Metadata")
    st.dataframe(df)

# Filter experiments by a selected column and value/range
def filter_experiments(df):
    st.write("### Filter Experiments")
    column_name = st.selectbox("Select column to filter", df.columns, index=df.columns.get_loc("experiment_name"))

    if df[column_name].dtype == 'object':
        unique_values = df[column_name].unique()
        selected_value = st.selectbox(f"Select {column_name} value", unique_values)
        filtered_df = df[df[column_name] == selected_value]
    else:
        min_value = float(df[column_name].min())
        max_value = float(df[column_name].max())
        if min_value == max_value:
            st.info(f"Only one unique value ({min_value}) in '{column_name}'.")
            filtered_df = df[df[column_name] == min_value]
        else:
            selected_range = st.slider(f"Select range for {column_name}", min_value, max_value, (min_value, max_value))
            filtered_df = df[(df[column_name] >= selected_range[0]) & (df[column_name] <= selected_range[1])]

    st.write("### Filtered Experiments")
    st.dataframe(filtered_df)
    return filtered_df

# Filter experiment data by selected column and value/range with flexible input
def filter_data(df):
    st.write("### Filter Data")
    column_name = st.selectbox("Select column to filter", df.columns)

    if df[column_name].dtype == 'object':
        unique_values = df[column_name].unique()
        selected_value = st.selectbox(f"Select {column_name} value", unique_values)
        filtered_df = df[df[column_name] == selected_value]
    else:
        min_value = float(df[column_name].min())
        max_value = float(df[column_name].max())
        st.write(f"Value range: {min_value:.2f} to {max_value:.2f}")

        col_left, col_right = st.columns([1, 3])
        with col_left:
            method = st.radio("Input Method", ["Slider", "Manual Input"], index=0)

        with col_right:
            if method == "Slider":
                selected_range = st.slider(
                    f"Select range for {column_name}",
                    min_value, max_value,
                    (min_value, max_value),
                    key=f"slider_{column_name}"
                )
            else:
                min_col, max_col = col_right.columns(2)
                min_input = min_col.number_input(f"Min {column_name}", value=min_value, step=0.1, key=f"min_input_{column_name}")
                max_input = max_col.number_input(f"Max {column_name}", value=max_value, step=0.1, key=f"max_input_{column_name}")
                selected_range = (min_input, max_input)

        filtered_df = df[(df[column_name] >= selected_range[0]) & (df[column_name] <= selected_range[1])]

    if st.checkbox("Show the filtered data"):
        st.write("### Filtered Data")
        selected_columns = st.multiselect("Select columns to display", filtered_df.columns.tolist(), default=filtered_df.columns.tolist(), key="filtered")
        st.dataframe(filtered_df[selected_columns])
    return filtered_df

# Plot selected columns from the dataframe with optional log scale on y-axis
def plot_data(df):
    st.write("### Plot Data")
    cols = st.columns(2)
    x_column = cols[0].selectbox("Select x-axis column", df.columns)
    y_column = cols[0].selectbox("Select y-axis column", df.columns)
    use_log_scale = cols[0].checkbox("Use log scale for y-axis", value=False)

    fig, ax = plt.subplots()
    ax.scatter(df[x_column], df[y_column])
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    if use_log_scale:
        ax.set_yscale('log')
    cols[1].pyplot(fig)
