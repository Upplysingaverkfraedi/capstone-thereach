import os
import requests
import pandas as pd
import argparse
import re
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and process football team data for a range of seasons.")
    parser.add_argument('--season', required=True, help="Season range in format 'YYYY-YYYY' (e.g., '2010-2024').")
    parser.add_argument('--debug', action='store_true', help="Save HTML for debugging.")
    return parser.parse_args()

def fetch_html(season):
    url = f"https://www.fotmob.com/en-GB/leagues/47/table/premier-league?season={season}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve data for season {season} from {url}")
        return None

def extract_json_data(html):
    match = re.search(r'"table":\s*(\{"all":.*?),"tableFilterTypes":\["all","home","away","form"(,"xg")?\]', html, re.DOTALL)
    
    if match:
        json_data = match.group(1)
        print("Extracted JSON data preview:", json_data[:500])
        
        try:
            data = json.loads(json_data)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON: {e}")
    else:
        raise ValueError("Failed to locate JSON data in the HTML.")

def process_section(data_section, output_filename, season):
    if not os.path.exists("Data"):
        os.makedirs("Data")

    teams = []
    for team in data_section:
        team_data = {
            "Name": team.get("name", team.get("teamName")),
            "Played": team["played"],
            "Wins": team["wins"],
            "Draws": team["draws"],
            "Losses": team["losses"],
            "GF": int(team["scoresStr"].split('-')[0]),
            "GA": int(team["scoresStr"].split('-')[1]),
            "GoalDiff": team.get("goalConDiff"),
            "Pts": team["pts"]
        }

        if "xg" in team:
            team_data.update({
                "xG": team["xg"],
                "xGConceded": team["xgConceded"],
                "xPoints": team["xPoints"],
                "xPosition": team.get("xPosition")
            })

        teams.append(team_data)

    df = pd.DataFrame(teams)
    df.to_csv(f"Data/{output_filename} {season}.csv", index=False)
    print(f"Data/{output_filename} {season}.csv has been created.")

def main():
    args = parse_arguments()

    # Parse the season range
    start_year, end_year = map(int, args.season.split('-'))
    for year in range(start_year, end_year):
        season = f"{year}-{year + 1}"

        html = fetch_html(season)
        if not html:
            print(f"Failed to fetch HTML data for season {season}. Skipping.")
            continue

        if args.debug:
            html_file = f"Data/{season}.html"
            with open(html_file, 'w', encoding='utf-8') as file:
                file.write(html)
            print(f"HTML for season {season} saved to {html_file}")

        data = extract_json_data(html)

        for section in ["all", "home", "away", "form", "xg"]:
            if section in data:
                process_section(data[section], section.capitalize(), season)

if __name__ == "__main__":
    main()
