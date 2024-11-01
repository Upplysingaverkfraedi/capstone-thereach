import requests
import pandas as pd
import argparse
import re
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description='Fetch and process football team data.')
    parser.add_argument('--url', help='URL to fetch data from.')
    parser.add_argument('--output', required=True, help='Output CSV file to save results.')
    parser.add_argument('--debug', action='store_true', help='Save HTML for debugging.')
    return parser.parse_args()

def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve data from {url}")
        return None

def extract_team_data(html):
    # Regex pattern to find JSON-like data in HTML
    pattern = re.compile(r'{"name":"(.*?)","shortName".*?"played":(\d+),"wins":(\d+),"draws":(\d+),"losses":(\d+),"scoresStr":"(\d+)-(\d+)","goalConDiff":(-?\d+),"pts":(\d+),"idx":\d+')
    matches = pattern.findall(html)
    
    # Debug: Print the matches to see if any data was found
    print("Matches found:", matches)
    
    # Convert matches to a structured dictionary if matches exist
    data = []
    if matches:
        for match in matches:
            name, played, wins, draws, losses, gf, ga, goal_diff, pts = match
            data.append({
                "Name": name,
                "Played": int(played),
                "Wins": int(wins),
                "Draws": int(draws),
                "Losses": int(losses),
                "GF": int(gf),
                "GA": int(ga),
                "GoalDiff": int(goal_diff),
                "Pts": int(pts)
            })
    else:
        print("No data found with the current pattern. Check if the data structure on the page has changed.")
    return data

def main():
    args = parse_arguments()

    html = fetch_html(args.url)
    if not html:
        raise Exception("Failed to fetch HTML data. Please check the URL.")
    
    if args.debug:
        html_file = args.output.replace('.csv', '.html')
        with open(html_file, 'w', encoding='utf-8') as file:
            file.write(html)
        print(f"HTML saved to {html_file}")

    # Extract team data from HTML
    team_data = extract_team_data(html)

    # Check if any data was found before trying to save to CSV
    if team_data:
        # Create DataFrame and save to CSV
        df = pd.DataFrame(team_data)
        df.to_csv(args.output, index=False)
        print(f"Data saved to {args.output}")
    else:
        print("No data to save. Please check the extraction step for issues.")

if __name__ == "__main__":
    main()
