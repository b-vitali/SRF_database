import sqlite3

# Function to open the database and fetch data
def check_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Query the database
    cursor.execute("SELECT * FROM data")
    
    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Print the rows (optional: you can format this output as needed)
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

# Call the function
check_database()
