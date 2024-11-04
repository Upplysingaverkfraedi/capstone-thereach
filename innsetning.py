import pandas as pd
import sqlite3
import glob

# Database file path
db_path = "premier_league.db"

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to load CSV data into match_status table
def load_csv_to_db(csv_file, season, status_type):
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Add the 'season' and 'status_type' columns
    df["season"] = season
    df["status_type"] = status_type

    # Reorder columns to match the database schema
    df = df[["Name", "Played", "Wins", "Draws", "Losses", "GF", "GA", "GoalDiff", "Pts", "season", "status_type"]]

    # Insert the data into match_status
    df.to_sql("match_status", conn, if_exists="append", index=False)
    print(f"Data from {csv_file} added to match_status table.")

# Load each CSV file
def process_csv_files(season):
    files = ["All", "Home", "Away"]
    for file_type in files:
        csv_file = f"{file_type} {season}.csv"
        load_csv_to_db(csv_file, season, file_type)

def main():
    seasons = [f"{year}-{year+1}" for year in range(2010, 2024)]  # Creates a list from 2010-2011 to 2023-2024
    for season in seasons:
        process_csv_files(season)

if __name__ == "__main__":
    main()

# Commit changes and close the connection
conn.commit()
conn.close()
