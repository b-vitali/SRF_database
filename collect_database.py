import sqlite3
import pandas as pd
import os
import json

def create_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Create experiments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL,
            lab_name TEXT,
            description TEXT,
            date TEXT,
            article_url TEXT
        );
    ''')

    # Create measurement data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            Time REAL,
            Temp REAL,
            MKS1000 REAL,
            LowerEdge1 REAL,
            Bandwidth REAL,
            Freq_raw REAL,
            Q0 REAL,
            LowerEdge2 REAL,
            Loss REAL,
            Max_Freq REAL,
            FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
        );
    ''')

    # Create plots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plots (
            plot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            file_path TEXT,
            caption TEXT,
            FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
        );
    ''')

    # Create processing steps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_steps (
            step_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            step_index INTEGER,
            process_type TEXT,
            description TEXT,
            temperature_c REAL,
            duration_h REAL,
            tags TEXT,
            FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
        );
    ''')

    conn.commit()
    conn.close()


def insert_experiment_metadata(experiment_name, lab_name, description, date, article_url=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Check if metadata already exists
    cursor.execute('''
        SELECT experiment_id FROM experiments
        WHERE experiment_name = ? AND date = ?
    ''', (experiment_name, date))
    existing = cursor.fetchone()

    if not existing:
        cursor.execute('''
            INSERT INTO experiments (experiment_name, lab_name, description, date, article_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (experiment_name, lab_name, description, date, article_url))

    conn.commit()
    conn.close()


def insert_csv_to_db(csv_file, experiment_id):
    df = pd.read_csv(csv_file, sep=r'\s+')
    df.columns = ["Time", "Temp", "MKS1000", "LowerEdge1", "Bandwidth", "Freq_raw", "Q0", "LowerEdge2", "Loss", "Max_Freq"]

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO data (experiment_id, Time, Temp, MKS1000, LowerEdge1, Bandwidth, Freq_raw, Q0, LowerEdge2, Loss, Max_Freq)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            experiment_id, row['Time'], row['Temp'], row['MKS1000'],
            row['LowerEdge1'], row['Bandwidth'], row['Freq_raw'],
            row['Q0'], row['LowerEdge2'], row['Loss'], row['Max_Freq']
        ))

    conn.commit()
    conn.close()


def insert_plot(experiment_id, file_path, caption=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO plots (experiment_id, file_path, caption)
        VALUES (?, ?, ?)
    ''', (experiment_id, file_path, caption))

    conn.commit()
    conn.close()


def import_experiment_from_folder(folder_path):
    metadata_path = os.path.join(folder_path, 'metadata.json')
    if not os.path.exists(metadata_path):
        print(f"No metadata.json in {folder_path}, skipping.")
        return

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    experiment_name = metadata['experiment_name']
    lab_name = metadata.get('lab_name', '')
    description = metadata.get('description', '')
    date = metadata['date']
    article_url = metadata.get('article_url', None)

    # Always insert experiment metadata first
    insert_experiment_metadata(experiment_name, lab_name, description, date, article_url)

    # Get experiment_id
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT experiment_id FROM experiments
        WHERE experiment_name = ? AND date = ?
        ORDER BY experiment_id DESC LIMIT 1
    ''', (experiment_name, date))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Failed to insert or retrieve experiment metadata.")
    experiment_id = row[0]

    # Insert processing steps if present
    processing_steps = metadata.get('processing_steps', [])
    for index, step in enumerate(processing_steps):
        cursor.execute('''
            INSERT INTO processing_steps (experiment_id, step_index, process_type, description, temperature_c, duration_h, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            experiment_id,
            index,
            step.get('process_type'),
            step.get('description'),
            step.get('temperature C'),
            step.get('duration h'),
            step.get('tags')
        ))

    conn.commit()
    conn.close()

    # Insert CSV data if available
    csv_file = None
    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            csv_file = os.path.join(folder_path, file)
            break
    if csv_file:
        insert_csv_to_db(csv_file, experiment_id)

    # Insert plots if any
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, file)
            insert_plot(experiment_id, file_path)


# ======================
# Example Usage
# ======================

# Step 1: Create database and tables
create_database()

# Step 2: Insert experiments from folders
import_experiment_from_folder("data/FG004_throughTc")
import_experiment_from_folder("data/FNAL_103")

# Step 3: Insert plot-only experiment
insert_experiment_metadata('FG005_no_data', 'Lab B', 'Lore lipsium (plot)', '2025-04-28')
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('SELECT experiment_id FROM experiments WHERE experiment_name = ? AND date = ?', ('FG005_no_data', '2025-04-28'))
experiment_id = cursor.fetchone()[0]
conn.close()

insert_plot(experiment_id, 'data/plot_dlambda_fit.png', caption='Overview of result')
insert_plot(experiment_id, 'data/plot_freq_q0_dual.png', caption='Zoomed region near Tc')
