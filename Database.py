import sqlite3
import pandas as pd
import os
import requests
import re
import json
import argparse


def create_database():
    """Creates the premier_league.db."""
    db_path = "premier_league.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create match_status table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_status (
        Name TEXT NOT NULL,
        Played INT,
        Wins INT,
        Draws INT,
        Losses INT,
        GF INT,
        GA INT,
        GoalDiff INT,
        Pts INT,
        season TEXT NOT NULL,
        status_type TEXT NOT NULL,
        PRIMARY KEY (Name, status_type, season)
    )
    ''')

    # Create Stadiums table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stadiums (
        Team TEXT PRIMARY KEY,
        FDCOUK TEXT,
        City TEXT,
        Stadium TEXT,
        Capacity INT,
        Latitude REAL,
        Longitude REAL,
        Country TEXT
    )
    ''')

    # Create Teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Team TEXT UNIQUE
    )
    ''')

    conn.commit()
    conn.close()
    print("Database and tables created.")


def load_games_table():
    """Loads all data from Games_season19-20.csv into the Games table."""
    conn = sqlite3.connect("premier_league.db")

    # Read the CSV file
    games_df = pd.read_csv('Games_season19-20.csv')

    # Dynamically create the Games table
    games_df.to_sql('Games', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    print("Games table created and populated with all data from the CSV.")


def filter_stadiums():
    """Filter and update the Stadiums table."""
    conn = sqlite3.connect("premier_league.db")
    cursor = conn.cursor()

    # Regex for Premier League teams
    team_pattern = re.compile(r'\b(?:Liverpool|Manchester City|Manchester United|Chelsea|Leicester City|'
                               r'Tottenham Hotspur|Wolverhampton Wanderers|Arsenal|Sheffield United|'
                               r'Burnley|Southampton|Everton|Newcastle United|Crystal Palace|'
                               r'Brighton & Hove Albion|West Ham United|Aston Villa|Bournemouth|'
                               r'Watford|Norwich City)\b')

    # Get all teams from the Stadiums table
    cursor.execute("SELECT Team FROM Stadiums")
    all_teams = [team[0] for team in cursor.fetchall()]

    # Identify teams to delete
    teams_to_keep = [team for team in all_teams if team_pattern.match(team)]
    teams_to_delete = [team for team in all_teams if team not in teams_to_keep]

    for team in teams_to_delete:
        cursor.execute("DELETE FROM Stadiums WHERE Team = ?", (team,))

    # Add missing teams
    missing_teams = [
        ("Bournemouth", "Bournemouth", "Vitality Stadium", 11379, 50.734841, -1.839080, "England"),
        ("Sheffield United", "Sheffield", "Bramall Lane", 32050, 53.370499, -1.470928, "England")
    ]
    for team in missing_teams:
        cursor.execute("SELECT 1 FROM Stadiums WHERE Team = ?", (team[0],))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO Stadiums (Team, FDCOUK, City, Stadium, Capacity, Latitude, Longitude, Country)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, team)

    conn.commit()
    conn.close()
    print("Stadiums table updated.")


def create_teams_table():
    """Create and populate the Teams table."""
    conn = sqlite3.connect("premier_league.db")
    cursor = conn.cursor()

    # Populate the Teams table with distinct team names from PlayerStats
    cursor.execute('''
    INSERT OR IGNORE INTO Teams (Team)
    SELECT DISTINCT Team FROM PlayerStats;
    ''')

    conn.commit()
    conn.close()
    print("Teams table created and populated.")


def load_additional_csvs():
    """Load additional CSVs into the database and clean up trailing spaces in Team names."""
    conn = sqlite3.connect("premier_league.db")
    cursor = conn.cursor()

    # Drop the Stadiums table to dynamically recreate it
    cursor.execute("DROP TABLE IF EXISTS Stadiums")

    # Load Premier League Player Stats.csv
    player_stats_df = pd.read_csv('Premier League Player Stats.csv')
    player_stats_df.to_sql('PlayerStats', conn, if_exists='replace', index=False)

    # Load stadiums-with-GPS-coordinates.csv
    stadiums_df = pd.read_csv('stadiums-with-GPS-coordinates.csv')

    # Trim whitespace from the Team column
    stadiums_df['Team'] = stadiums_df['Team'].str.strip()

    # Dynamically recreate the Stadiums table with all columns from the CSV
    stadiums_df.to_sql('Stadiums', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    print("Additional CSV data loaded into the database with cleaned Team names.")


def fetch_fotmob_data(season):
    """Fetch and process football team data for a given season."""
    url = f"https://www.fotmob.com/en-GB/leagues/47/table/premier-league?season={season}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for season {season}.")
        return None

    html = response.text
    match = re.search(r'"table":\s*(\{"all":.*?),"tableFilterTypes":\[', html, re.DOTALL)
    if not match:
        print("Failed to extract JSON data.")
        return None

    json_data = match.group(1)
    try:
        data = json.loads(json_data)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def process_fotmob_data(data, section, season):
    """Process FotMob data and save it to the database."""
    conn = sqlite3.connect("premier_league.db")
    teams = []

    for team in data[section]:
        team_data = {
            "Name": team.get("name", team.get("teamName")),
            "Played": team["played"],
            "Wins": team["wins"],
            "Draws": team["draws"],
            "Losses": team["losses"],
            "GF": int(team["scoresStr"].split('-')[0]),
            "GA": int(team["scoresStr"].split('-')[1]),
            "GoalDiff": team.get("goalConDiff"),
            "Pts": team["pts"],
            "season": season,
            "status_type": section.capitalize()
        }
        teams.append(team_data)

    df = pd.DataFrame(teams)
    df.to_sql('match_status', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    print(f"Processed {section} data for season {season}.")


def main():
    parser = argparse.ArgumentParser(description="Fetch and process football data.")
    parser.add_argument("--season", required=True, help="Season range in format 'YYYY-YYYY' (e.g., '2010-2024').")
    parser.add_argument("--debug", action="store_true", help="Save HTML for debugging.")
    args = parser.parse_args()

    create_database()
    load_games_table()
    load_additional_csvs()
    filter_stadiums()
    create_teams_table()

    # Fetch and process FotMob data
    start_year, end_year = map(int, args.season.split('-'))
    for year in range(start_year, end_year):
        season = f"{year}-{year + 1}"
        data = fetch_fotmob_data(season)
        if data:
            for section in ["all", "home", "away"]:
                if section in data:
                    process_fotmob_data(data, section, season)

    print("All tasks completed. Database is ready.")


if __name__ == "__main__":
    main()
