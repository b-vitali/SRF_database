import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

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

# Display the experiments in the UI
def display_experiments(df):
    st.write("### Experiments Metadata")
    st.dataframe(df)

# Function to filter experiments by name or lab
def filter_experiments(df):
    st.write("### Filter Experiments")

    # Select column for filtering
    column_name = st.selectbox("Select column to filter", df.columns)
    
    # Dynamically filter based on column type
    if df[column_name].dtype == 'object':  # For categorical columns
        unique_values = df[column_name].unique()
        selected_value = st.selectbox(f"Select {column_name} value", unique_values)
        filtered_df = df[df[column_name] == selected_value]
    else:  # For numeric columns
        min_value = float(df[column_name].min())
        max_value = float(df[column_name].max())
        selected_range = st.slider(f"Select range for {column_name}", min_value, max_value, (min_value, max_value))
        filtered_df = df[(df[column_name] >= selected_range[0]) & (df[column_name] <= selected_range[1])]
    
    st.write("### Filtered Experiments")
    st.dataframe(filtered_df)
    return filtered_df

# Function to filter data based on user input (for experiment data)
def filter_data(df):
    st.write("### Filter Data")

    # Select column for filtering
    column_name = st.selectbox("Select column to filter", df.columns)
    
    # Dynamically filter based on column type
    if df[column_name].dtype == 'object':  # For categorical columns
        unique_values = df[column_name].unique()
        selected_value = st.selectbox(f"Select {column_name} value", unique_values)
        filtered_df = df[df[column_name] == selected_value]
    else:  # For numeric columns
        min_value = float(df[column_name].min())
        max_value = float(df[column_name].max())
        selected_range = st.slider(f"Select range for {column_name}", min_value, max_value, (min_value, max_value))
        filtered_df = df[(df[column_name] >= selected_range[0]) & (df[column_name] <= selected_range[1])]
    
    st.write("### Filtered Data")
    st.dataframe(filtered_df)
    return filtered_df

# Function to plot data
def plot_data(df):
    st.write("### Plot Data")
    
    # Let the user select the plot type
    plot_type = st.selectbox("Select plot type", ["Scatter", "Line", "Bar"])
    
    # Select columns for x and y axes
    x_column = st.selectbox("Select x-axis column", df.columns)
    y_column = st.selectbox("Select y-axis column", df.columns)
    

    if plot_type == "Scatter":
        fig, ax = plt.subplots()
        ax.scatter(df[x_column], df[y_column])
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        st.pyplot(fig)
    elif plot_type == "Line":
        st.line_chart(df[[x_column, y_column]])
    elif plot_type == "Bar":
        st.bar_chart(df[[x_column, y_column]])

# Main app function
def main():
    st.title("Experiment Data Query and Visualization")
    st.write("Current working directory:", os.getcwd())

    # Load the experiments metadata
    experiments_df = load_experiments()
    
    # Display the experiments metadata
    display_experiments(experiments_df)
    
    # Filter experiments based on user selection
    filtered_experiments_df = filter_experiments(experiments_df)
    
    # If there are filtered experiments, allow the user to select one and load the corresponding data
    if not filtered_experiments_df.empty:
        experiment_name = st.selectbox("Select Experiment", filtered_experiments_df['experiment_name'])
        
        # Get the experiment_id of the selected experiment
        experiment_id = filtered_experiments_df[filtered_experiments_df['experiment_name'] == experiment_name]['experiment_id'].iloc[0]
        
        # Load the data for the selected experiment
        experiment_data_df = load_data_for_experiment(experiment_id)
        
        # Display the data for the selected experiment
        st.write(f"### Data for Experiment: {experiment_name}")
        st.dataframe(experiment_data_df)
        
        # Filter and plot the data for the selected experiment
        if not experiment_data_df.empty:
            filtered_data_df = filter_data(experiment_data_df)
            plot_data(filtered_data_df)
        
        # Load and display plots for the selected experiment
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
