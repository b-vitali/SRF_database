import sqlite3
import pandas as pd

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

    conn.commit()
    conn.close()

import os
import json

def import_experiment_from_folder(folder_path):
    # Load metadata from JSON
    metadata_path = os.path.join(folder_path, 'metadata.json')
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    experiment_name = metadata['experiment_name']
    lab_name = metadata.get('lab_name', '')
    description = metadata.get('description', '')
    date = metadata['date']
    article_url = metadata.get('article_url', None)

    # Look for a CSV file
    csv_file = None
    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            csv_file = os.path.join(folder_path, file)
            break

    # Insert metadata and data
    if csv_file:
        insert_csv_to_db(csv_file, experiment_name, lab_name, description, date, article_url)
    else:
        insert_experiment_metadata(experiment_name, lab_name, description, date, article_url)

    # Insert plots
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, file)
            insert_plot(experiment_name, date, os.path.join(folder_path, file))



def insert_experiment_metadata(experiment_name, lab_name, description, date, article_url=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO experiments (experiment_name, lab_name, description, date, article_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (experiment_name, lab_name, description, date, article_url))
    
    conn.commit()
    conn.close()

def insert_csv_to_db(csv_file, experiment_name, lab_name, description, date, article_url=None):
    # Read CSV file
    df = pd.read_csv(csv_file, sep=r'\s+')
    df.columns = ["Time", "Temp", "MKS1000", "LowerEdge1", "Bandwidth", "Freq_raw", "Q0", "LowerEdge2", "Loss", "Max_Freq"]
    
    # Insert experiment metadata
    insert_experiment_metadata(experiment_name, lab_name, description, date, article_url)
    
    # Retrieve experiment_id
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT experiment_id FROM experiments
        WHERE experiment_name = ? AND date = ?
        ORDER BY experiment_id DESC LIMIT 1
    ''', (experiment_name, date))
    experiment_id = cursor.fetchone()[0]
    
    # Insert measurement rows
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO data (experiment_id, Time, Temp, MKS1000, LowerEdge1, Bandwidth, Freq_raw, Q0, LowerEdge2, Loss, Max_Freq)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, row['Time'], row['Temp'], row['MKS1000'], row['LowerEdge1'], row['Bandwidth'],
              row['Freq_raw'], row['Q0'], row['LowerEdge2'], row['Loss'], row['Max_Freq']))
    
    conn.commit()
    conn.close()

def insert_plot(experiment_name, date, file_path, caption=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Retrieve experiment_id
    cursor.execute('''
        SELECT experiment_id FROM experiments
        WHERE experiment_name = ? AND date = ?
        ORDER BY experiment_id DESC LIMIT 1
    ''', (experiment_name, date))
    
    result = cursor.fetchone()
    if result is None:
        raise ValueError("Experiment not found. Insert metadata first.")
    
    experiment_id = result[0]
    
    # Insert plot record
    cursor.execute('''
        INSERT INTO plots (experiment_id, file_path, caption)
        VALUES (?, ?, ?)
    ''', (experiment_id, file_path, caption))
    
    conn.commit()
    conn.close()

# ======================
# Example Usage
# ======================

# Step 1: Create database and tables
create_database()

# Step 2: Insert CSV-based experiments
insert_csv_to_db('data/20250128_FNAL_103.txt', '20250128_FNAL_103', 'FNAL', 'Lore lipsium (data)', '2025-01-28', article_url='https://arxiv.org/abs/2401.12345')
insert_csv_to_db('data/20250128_FNAL_103.txt', '20250128_FNAL_103_copy', 'FNAL', 'Lore lipsium (data)', '2025-01-28', article_url='https://arxiv.org/abs/2401.12345')

import_experiment_from_folder("data/FG004_throughTc")

# Step 3: Insert plot-only experiment
insert_experiment_metadata('FG005_no_data', 'Lab B', 'Lore lipsium (plot)', '2025-04-28')
insert_plot('FG005_no_data', '2025-04-28', 'data/plot_dlambda_fit.png', caption='Overview of result')
insert_plot('FG005_no_data', '2025-04-28', 'data/plot_freq_q0_dual.png', caption='Zoomed region near Tc')
