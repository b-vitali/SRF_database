import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Define simple credentials
USER_CREDENTIALS = {
    "lasa": "2025"
}

# Function to handle login
def login():
    st.title("Login Page")

    # Check if the user is already logged in
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
    conn = sqlite3.connect('data.db')
    query = "SELECT * FROM experiments"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load data from the database for a specific experiment
def load_data_for_experiment(experiment_id):
    conn = sqlite3.connect('data.db')
    query = f"SELECT * FROM data WHERE experiment_id = {experiment_id}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load plots from the database for a specific experiment
def load_plots_for_experiment(experiment_id):
    conn = sqlite3.connect('data.db')
    query = f"SELECT * FROM plots WHERE experiment_id = {experiment_id}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load processing steps for a specific experiment
def load_processing_steps_for_experiment(experiment_id):
    conn = sqlite3.connect('data.db')
    query = f"SELECT * FROM processing_steps WHERE experiment_id = {experiment_id} ORDER BY step_index ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Function to get experiments that have processing steps containing a specific tag
def get_experiments_by_processing_tag(tag):
    conn = sqlite3.connect('data.db')
    query = """
        SELECT DISTINCT experiment_id
        FROM processing_steps
        WHERE tags LIKE ?
    """
    df = pd.read_sql(query, conn, params=(f"%{tag}%",))
    conn.close()
    return df['experiment_id'].tolist()

def get_all_processing_tags():
    conn = sqlite3.connect('data.db')
    query = "SELECT DISTINCT tag FROM processing_steps WHERE tag IS NOT NULL"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Return sorted list of tags
    return sorted(df['tag'].dropna().unique())

def get_all_processing_tags():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tags FROM processing_steps")
    rows = cursor.fetchall()
    conn.close()

    return sorted(tag[0] for tag in rows if tag[0])

# Display the experiments in the UI
def display_experiments(df):
    st.write("### Experiments Metadata")
    st.dataframe(df)

# Function to filter experiments by name or lab
def filter_experiments(df):
    st.write("### Filter Experiments")

    # Select column for filtering, default to 'experiment_name'
    column_name = st.selectbox("Select column to filter", df.columns, index=df.columns.get_loc("experiment_name"))
    
    # Dynamically filter based on column type
    if df[column_name].dtype == 'object':  # For categorical columns
        unique_values = df[column_name].unique()
        selected_value = st.selectbox(f"Select {column_name} value", unique_values)
        filtered_df = df[df[column_name] == selected_value]
    else:  # For numeric columns
        min_value = float(df[column_name].min())
        max_value = float(df[column_name].max())
        if min_value == max_value:
            st.info(f"Only one unique value ({min_value}) available in '{column_name}'. Showing all matching rows.")
            filtered_df = df[df[column_name] == min_value]
        else:
            selected_range = st.slider(f"Select range for {column_name}", min_value, max_value, (min_value, max_value))
            filtered_df = df[(df[column_name] >= selected_range[0]) & (df[column_name] <= selected_range[1])]
    
    st.write("### Filtered Experiments")
    st.dataframe(filtered_df)
    return filtered_df


# Function to filter data based on user input (for experiment data)
def filter_data(df):
    st.write("### Filter Data")

    # Select column for filtering default to 'Temp'
    column_name = st.selectbox("Select column to filter", df.columns, index=df.columns.get_loc("Temp"))
    
    # Dynamically filter based on column type
    if df[column_name].dtype == 'object':  # For categorical columns
        unique_values = df[column_name].unique()
        selected_value = st.selectbox(f"Select {column_name} value", unique_values)
        filtered_df = df[df[column_name] == selected_value]
    else:  # For numeric columns
        min_value = float(df[column_name].min())
        max_value = float(df[column_name].max())
        st.write(f"Value range in data: {min_value:.2f} to {max_value:.2f}")
        
        # Two top-level columns: Left for method, Right for inputs
        col_left, col_right = st.columns([1, 3])

        with col_left:
            use_manual_input = st.radio("Input Method", ["Slider", "Manual Input"], index=0)

        with col_right:
            if use_manual_input == "Slider":
                selected_range = st.slider(
                    f"Select range for {column_name}",
                    min_value, max_value,
                    (min_value, max_value),
                    key=f"slider_{column_name}"
                )
            else:
                # Split the right column into two for Min and Max input fields
                min_col, max_col = col_right.columns(2)
                min_input = min_col.number_input(
                    f"Min {column_name}", value=min_value, step=0.1, key=f"min_input_{column_name}"
                )
                max_input = max_col.number_input(
                    f"Max {column_name}", value=max_value, step=0.1, key=f"max_input_{column_name}"
                )
                selected_range = (min_input, max_input)

        # Apply the filter
        filtered_df = df[
            (df[column_name] >= selected_range[0]) &
            (df[column_name] <= selected_range[1])
        ]

    
    if st.checkbox("Show the filtered data"):
        st.write("### Filtered Data")
        selected_columns = st.multiselect("Select columns to display", filtered_df.columns.tolist(), default=filtered_df.columns.tolist())
        st.dataframe(filtered_df[selected_columns])
    return filtered_df

# Function to plot data
def plot_data(df):
    st.write("### Plot Data")
    cols = st.columns(2)
    # Select columns for x and y axes defalut to 'Temp' and 'Q0'
    x_column = cols[0].selectbox("Select x-axis column", df.columns, index=df.columns.get_loc("Temp"))
    y_column = cols[0].selectbox("Select y-axis column", df.columns, index=df.columns.get_loc("Q0"))
    
    use_log_scale = cols[0].checkbox("Use log scale for y-axis", value=False)

    fig, ax = plt.subplots()
    ax.scatter(df[x_column], df[y_column])
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    if use_log_scale:
        ax.set_yscale('log')
    cols[1].pyplot(fig)

# Main app function
def main():
    # Check if the user is logged in
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        if not login():
            return  # If not logged in, show the login page and exit
    
    st.title("Experiment Data Query and Visualization")
    st.write("Current working directory:", os.getcwd())

    # Load the experiments metadata
    experiments_df = load_experiments()
    
    if st.checkbox("Filter Experiments by Processing Step Tags"):
        # Get all unique tags from the database
        all_tags = get_all_processing_tags()

        # Initialize selected tags in session state
        if "selected_tags" not in st.session_state:
            st.session_state["selected_tags"] = []

        st.write("### Click on tags to add/remove them from filter:")
        # Dynamically determine number of columns
        num_tags = len(all_tags)
        cols = st.columns(num_tags)

        for idx, tag in enumerate(all_tags):
            col = cols[idx % 6]
            if tag in st.session_state["selected_tags"]:
                if col.button(f"✅ {tag}", key=f"tag_selected_{tag}"):
                    st.session_state["selected_tags"].remove(tag)
                    st.rerun()
            else:
                if col.button(f"⬜ {tag}", key=f"tag_unselected_{tag}"):
                    st.session_state["selected_tags"].append(tag)
                    st.rerun()

        # Show selected tags
        selected_tags = st.session_state["selected_tags"]
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

    # Display the experiments metadata
    display_experiments(experiments_df)
    
    # Filter experiments based on user selection
    if st.checkbox("Filter by metadata information"):        
        filtered_experiments_df = filter_experiments(experiments_df)
    else:
        filtered_experiments_df = experiments_df

    # If there are filtered experiments, allow the user to select one and load the corresponding data
    if not filtered_experiments_df.empty:
        experiment_name = st.selectbox("Select Experiment", filtered_experiments_df['experiment_name'])
        
        # Get the experiment_id of the selected experiment
        experiment_id = filtered_experiments_df[filtered_experiments_df['experiment_name'] == experiment_name]['experiment_id'].iloc[0]
        
        # Load and display processing steps
        processing_df = load_processing_steps_for_experiment(experiment_id)
        if not processing_df.empty and st.checkbox("Show Processing Steps Table"):
            st.write("### Processing Steps")
            selected_columns = ["process_type","description","temperature_c","duration_h","tags"]
            st.dataframe(processing_df[selected_columns])

        # Load the data for the selected experiment
        experiment_data_df = load_data_for_experiment(experiment_id)
        
        # Optional display of raw data for the selected experiment
        if st.checkbox("Show Raw Data Table"):
            st.write(f"### Data for Experiment: {experiment_name}")
            selected_columns = st.multiselect("Select columns to display", experiment_data_df.columns.tolist(), default=experiment_data_df.columns.tolist())
            st.dataframe(experiment_data_df[selected_columns])

        # Filter and plot the data for the selected experiment
        if not experiment_data_df.empty and st.checkbox("Filter the raw data and plot"):
            filtered_data_df = filter_data(experiment_data_df)
            plot_data(filtered_data_df)
        
        # Load and display plots for the selected experiment
        if st.checkbox("Load png plots"):        
            plots_df = load_plots_for_experiment(experiment_id)
            if not plots_df.empty:
                st.write("### Associated Plots")
                for _, row in plots_df.iterrows():
                    if os.path.exists(row['file_path']):
                        st.image(row['file_path'], caption=row['caption'] if row['caption'] else "", use_container_width=True)
                    else:
                        st.warning(f"Image file not found: {row['file_path']}")

# Entry point
if __name__ == "__main__":
    main()
