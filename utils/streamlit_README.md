# Database for SRF cavities
This project wants to be a database of the test results of SRF cavities

The main idea is the following:
1. Use a combination of `python` + `SQLite` to collect the data
2. Use a `python` based UI to query, browse and visualize the data

## Use
This streamlit UI interface has 3 main sections
1. A quary/plotting inteface to navigate the existing `data/srf_database.db`
1. A UI to help you generate new data in the correct format 
  NB: to update the database you need to run locally `python collect_database.py`
1. This README to help you out

### 1 Query and plot

The **Browse** section of the Streamlit app is the interface for querying and visualizing the SRF database stored in `data/srf_database.db`.

This interface allows you to:

1. **Log in**  
   User authentication (if required to access the database).

2. **Browse all experiments**  
   Once logged in, you can view a list of all recorded experiments and their metadata.

3. **Filter by processing tags**  
   You can filter experiments by selecting one or more tags that correspond to the processing steps applied to the cavity (e.g., "bake", "nitrogen").

4. **Filter by metadata**  
   Further refine your search using metadata fields such as lab name, date, etc.

5. **Select and inspect an experiment**  
   Choose a specific experiment from the list to view its details.

   - **Processing steps**: If available, a table of the applied processing steps can be displayed.
   - **Raw data**: Shows the experimental data in tabular form. You can select which columns to display.
   - **Data filtering**: Optionally apply filters to the raw data table (e.g., range selections).
   - **Plotting**: Select columns from the data to generate plots directly in the interface.
   - **Associated images**: Load and display images (e.g., PNG plots) associated with the experiment.

This interface is ideal for data exploration and visualization of stored SRF cavity test results.


### 2 New data

The **Create** page provides a guided interface to generate a `.zip` archive containing metadata, raw data, and optional images for a new SRF cavity experiment. This archive is formatted to be compatible with the database update script (`collect_database.py`).

**Un-zip it** before placing in the `data` folder

Steps to use:

1. **Fill in Experiment Info**  
   Provide the experiment name, lab name, description, date, and (optionally) a related article URL. This information forms the core metadata.

2. **(Optional) Define processing steps** 
   Check the "Define processing steps" box to add detailed steps applied to the cavity (e.g., baking, coating). Each step can include a process type, temperature, duration, tags, and a short description. You can reorder, insert, or remove steps as needed.

3. **(Optional) Include raw data**  
   Check the "Include Raw Data" box to attach experimental data in plain text format. Provide a base filename and paste the raw tabular data into the text box.

4. **(Optional) Attach images**  
   Check the "Attach images" box to upload one or more PNG or JPEG images (e.g., plots, photos). You can reorder or remove images before packaging.

5. **Generate and Download**  
   Click "Generate and Download Data ZIP" to create a `.zip` file containing all entered information. Use this file with `collect_database.py` to insert it into the main database.

   **Un-zip it** before placing in the `data` folder
