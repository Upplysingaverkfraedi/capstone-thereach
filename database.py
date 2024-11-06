import sqlite3
import pandas as pd

# Load the CSV files into DataFrames
games_df = pd.read_csv('Games_season19-20.csv')
player_stats_df = pd.read_csv('Premier League Player Stats.csv')
stadiums_df = pd.read_csv('stadiums-with-GPS-coordinates.csv')

# Create a new SQLite database (or connect to an existing one)
conn = sqlite3.connect('premier_league.db')
cursor = conn.cursor()


# Insert the data into the database
games_df.to_sql('Games', conn, if_exists='append', index=False)
player_stats_df.to_sql('PlayerStats', conn, if_exists='append', index=False)
stadiums_df.to_sql('Stadiums', conn, if_exists='append', index=False)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database creation and data import completed.")

