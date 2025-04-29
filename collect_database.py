import sqlite3
import pandas as pd

def create_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Add article_url column to experiments table if not already there
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
    
    conn.commit()
    conn.close()

def insert_experiment_metadata(experiment_name, lab_name, description, date, article_url):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO experiments (experiment_name, lab_name, description, date, article_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (experiment_name, lab_name, description, date, article_url))
    
    conn.commit()
    conn.close()

def insert_csv_to_db(csv_file, experiment_name, lab_name, description, date, article_url=None):
    # Read the CSV file
    df = pd.read_csv(csv_file, sep=r'\s+')
    df.columns = ["Time", "Temp", "MKS1000", "LowerEdge1", "Bandwidth", "Freq_raw", "Q0", "LowerEdge2", "Loss", "Max_Freq"]
    
    # Insert metadata
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
    
    # Insert measurements
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO data (experiment_id, Time, Temp, MKS1000, LowerEdge1, Bandwidth, Freq_raw, Q0, LowerEdge2, Loss, Max_Freq)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, row['Time'], row['Temp'], row['MKS1000'], row['LowerEdge1'], row['Bandwidth'],
              row['Freq_raw'], row['Q0'], row['LowerEdge2'], row['Loss'], row['Max_Freq']))
    
    conn.commit()
    conn.close()


# Example usage
create_database()
insert_csv_to_db('data/20250128_FNAL_103.txt', '20250128_FNAL_103', 'FNAL', 'Experiment on test subject 103', '2025-01-28', article_url='https://arxiv.org/abs/2401.12345')
insert_csv_to_db('data/20250128_FNAL_103.txt', '20250128_FNAL_103_copy', 'FNAL', 'Experiment on test subject 103bis', '2025-01-28', article_url='https://arxiv.org/abs/2401.12345')
insert_csv_to_db('data/FG004_throughTc.txt', 'FG004_throughTc', 'Lab A', 'Test data of FG004 through Tc', '2025-04-01', article_url='https://arxiv.org/abs/2401.12342')
