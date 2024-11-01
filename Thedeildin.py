import requests
import pandas as pd
import argparse
import re
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and process football team data for a given season.")
    parser.add_argument('--season', required=True, help="Season to fetch data for, in format 'YYYY-YYYY' (e.g., '2024-2025').")
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
    # Match the JSON data inside the "table" object from "all" to the closing of "xg"
    match = re.search(r'"table":\s*(\{"all":.*?,"xg":\[.*?\]\})', html, re.DOTALL)
    
    if match:
        json_data = match.group(1)
        # Debug: Print the extracted JSON snippet (optional)
        print("Extracted JSON data preview:", json_data[:500])
        
        try:
            data = json.loads(json_data)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON: {e}")
    else:
        raise ValueError("Failed to locate JSON data in the HTML.")


def process_section(data_section, output_filename, season):
    teams = []
    for team in data_section:
        # Handle sections with additional fields based on the available data.
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

        # Additional fields for the xG table
        if "xg" in team:
            team_data.update({
                "xG": team["xg"],
                "xGConceded": team["xgConceded"],
                "xPoints": team["xPoints"],
                "xPosition": team.get("xPosition")
            })

        teams.append(team_data)

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(teams)
    df.to_csv(f"{output_filename} {season}.csv", index=False)
    print(f"{output_filename} {season}.csv has been created.")

def main():
    args = parse_arguments()

    # Fetch HTML for the given season
    html = fetch_html(args.season)
    if not html:
        raise Exception("Failed to fetch HTML data. Please check the season.")

    if args.debug:
        html_file = f"{args.season}.html"
        with open(html_file, 'w', encoding='utf-8') as file:
            file.write(html)
        print(f"HTML for season {args.season} saved to {html_file}")

    # Extract JSON data from HTML
    data = extract_json_data(html)

    # Process each section and save to CSV with the season in the filename
    for section in ["all", "home", "away", "form", "xg"]:
        if section in data:
            process_section(data[section], section.capitalize(), args.season)

if __name__ == "__main__":
    main()
