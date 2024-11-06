import sqlite3
import pandas as pd
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_plotly
import plotly.express as px
import re
import matplotlib.pyplot as plt
import tempfile


# Database setup: Load CSV files into a SQLite database
db_path = 'premier_league.db'
conn = sqlite3.connect(db_path)

# Load CSV files into DataFrames
games_df = pd.read_csv('Games_season19-20.csv')
player_stats_df = pd.read_csv('Premier League Player Stats.csv')
stadiums_df = pd.read_csv('stadiums-with-GPS-coordinates.csv')

# Define the regex pattern for filtering 2019/20 Premier League teams
pattern = r'\b(?:Liverpool|Manchester City|Manchester United|Chelsea|Leicester City|Tottenham Hotspur|Wolverhampton Wanderers|Arsenal|Sheffield United|Burnley|Southampton|Everton|Newcastle United|Crystal Palace|Brighton and Hove Albion|West Ham United|Aston Villa|Bournemouth|Watford|Norwich City)\b'

# Filter the stadiums DataFrame for only 2019/20 Premier League teams
stadiums_df = stadiums_df[stadiums_df['Team'].str.contains(pattern, case=False)]

# Drop tables if they exist to ensure fresh import
conn.execute("DROP TABLE IF EXISTS Games")
conn.execute("DROP TABLE IF EXISTS PlayerStats")
conn.execute("DROP TABLE IF EXISTS Stadiums")

# Insert the data into the database
games_df.to_sql('Games', conn, if_exists='replace', index=False)
player_stats_df.to_sql('PlayerStats', conn, if_exists='replace', index=False)
stadiums_df.to_sql('Stadiums', conn, if_exists='replace', index=False)

# Commit the changes and close the connection
conn.commit()
conn.close()
print("Database and tables created, and data imported.")

app_ui = ui.page_fluid(
    ui.tags.style("""
        /* Light mode styles */
        body.light-mode {
            background-color: #ffffff;
            color: #000000;
        }
        /* Dark mode styles */
        body.dark-mode {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        /* Table and other component styles for dark mode */
        .slider-container, .dropdown-menu, .table, .navbar, .card, .panel {
            background-color: #333333;
            color: #e0e0e0;
        }
        table.dataframe th, table.dataframe td {
            border: 1px solid #444444;
            color: #e0e0e0;
            background-color: #333333;
        }
        table.dataframe th {
            background-color: #4CAF50;
            color: white;
        }
        table.dataframe tr:nth-child(even) {
            background-color: #2a2a2a;
        }
        table.dataframe tr:hover {
            background-color: #444444;
        }
    """),

    ui.tags.div(
        {
            "style": """
                background: linear-gradient(135deg, #38003c, #4CAF50);
                padding: 20px;
                text-align: center;
                border-radius: 8px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
                color: #ffffff;
            """
        },
        ui.h1("Enska Úrvalsdeildin", style="font-size: 3em; font-weight: bold; margin: 0;"),
        ui.h3("2019/20", style="font-size: 1.5em; font-weight: normal; color: #d0d0d0; margin-top: 5px;")
    ),

    ui.navset_tab(
        ui.nav_panel(
            "Heim",
            ui.h2("Premier League Home"),
            ui.p("Welcome to the Premier League Analysis."),
            ui.input_switch("theme_switch", "Dark Mode", False),
            ui.tags.script(
                """
                document.getElementById('theme_switch').addEventListener('change', function() {
                    if (this.checked) {
                        document.body.classList.add('dark-mode');
                        document.body.classList.remove('light-mode');
                    } else {
                        document.body.classList.add('light-mode');
                        document.body.classList.remove('dark-mode');
                    }
                });
                """
            )
        ),
        ui.nav_panel(
            "Stöðutafla",
            ui.h2("Tímabilið 2019/20"),

            # Adjusted slider container for "Veldu tímabilsviku"
            ui.tags.div(
                {"class": "slider-container", "style": "padding: 10px; max-width: 400px; margin-bottom: 20px;"},
                ui.input_slider("game_week", "Veldu tímabilsviku:", min=1, max=38, value=1)
            ),

            ui.row(
                ui.column(6,
                    ui.tags.div(
                        {"id": "score_table"},
                        ui.output_table("score_table", escape=False)
                    ),
                ),
                ui.column(6,
                    ui.input_select("team_select", "Veldu lið", choices=sorted(games_df['HomeTeam'].unique()), selected="Liverpool"),

                    # Adjusted slider container for "Veldu fjölda síðustu leikja"
                    ui.tags.div(
                        {"class": "slider-container", "style": "padding: 10px; max-width: 400px; margin-bottom: 20px;"},
                        ui.input_slider("num_games", "Veldu fjölda síðustu leikja", min=1, max=10, value=5)
                    ),

                    ui.output_table("last_games_table")
                )
            )
        ),
        ui.nav_panel(
            "Staðsetningar",
            ui.h2("Stadiums with GPS Coordinates"),
            output_widget("stadiums_map"),
            ui.p("Map of stadiums in the Premier League with GPS coordinates.")
        ),
        ui.nav_panel(
            "Færanýtni",
            ui.h2("Player Efficiency"),
            ui.input_select("plot_choice", "Veldu tegund af scatter plot:", choices=["Goals vs. Minutes", "Shots on Target vs. Goals", "Top Goalscorers"]),
            ui.input_slider("top_n_scorers", "Veldu fjölda af markahæstu leikmönnum:", min=1, max=251, value=10),
            output_widget("efficiency_plot")
        ),
        ui.nav_panel(
            "BetStatistics",
            ui.h2("Betting Stats fyrir valið lið"),

            # Input select for team selection
            ui.input_select("bet_team_select", "Veldu lið", choices=sorted(games_df['HomeTeam'].unique()), selected="Liverpool"),

            # Flex container to align the plot and profit/loss box side by side
            ui.tags.div(
                {"style": "display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 20px;"},

                # Betting progress plot
                ui.tags.div(
                    {"style": "flex: 2;"},
                    ui.output_plot("betting_progress_plot")
                ),

                # End-of-season profit/loss box with ui.output_text to prevent scrolling
                ui.tags.div(
                    {"style": """
                        background-color: #333333;
                        color: #e0e0e0;
                        padding: 15px;
                        text-align: center;
                        border-radius: 8px;
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
                        font-size: 1.25em;
                        max-width: 200px;
                    """},
                    ui.output_text("end_season_profit_loss")
                )
            )
        )
    )
)





# Define function to calculate league table for a specific game week
def calculate_league_table(games_df, game_week):
    teams_data = {}

    # Filter games up to the selected game week
    weekly_games = games_df[games_df['GW'] <= game_week]

    for _, row in weekly_games.iterrows():
        home_team, away_team = row['HomeTeam'], row['AwayTeam']
        home_goals, away_goals = row['FTHG'], row['FTAG']
        result = row['FTR']

        if home_team not in teams_data:
            teams_data[home_team] = {"Played": 0, "W": 0, "D": 0, "L": 0, "+/-": 0, "PTS": 0}
        if away_team not in teams_data:
            teams_data[away_team] = {"Played": 0, "W": 0, "D": 0, "L": 0, "+/-": 0, "PTS": 0}

        # Update matches played and goals for each team
        teams_data[home_team]["Played"] += 1
        teams_data[away_team]["Played"] += 1
        teams_data[home_team]["+/-"] += (home_goals - away_goals)
        teams_data[away_team]["+/-"] += (away_goals - home_goals)

        # Determine result for home and away teams
        if result == "H":
            teams_data[home_team]["W"] += 1
            teams_data[home_team]["PTS"] += 3
            teams_data[away_team]["L"] += 1
        elif result == "A":
            teams_data[away_team]["W"] += 1
            teams_data[away_team]["PTS"] += 3
            teams_data[home_team]["L"] += 1
        else:
            teams_data[home_team]["D"] += 1
            teams_data[away_team]["D"] += 1
            teams_data[home_team]["PTS"] += 1
            teams_data[away_team]["PTS"] += 1

    # Convert teams_data to a DataFrame and sort by Points and GD
    league_table_df = pd.DataFrame.from_dict(teams_data, orient="index")
    league_table_df = league_table_df.sort_values(by=["PTS", "+/-"], ascending=[False, False]).reset_index()
    league_table_df.rename(columns={"index": "Team"}, inplace=True)
    league_table_df['POS'] = league_table_df.index + 1  # Adding position for display
    return league_table_df

# Function to get the last N games (including the current week) for a selected team
def get_last_n_games(team, game_week, num_games):
    # Filter games involving the selected team up to and including the current game week
    team_games = games_df[(games_df['HomeTeam'] == team) | (games_df['AwayTeam'] == team)]
    team_games = team_games[team_games['GW'] <= game_week].sort_values(by="GW", ascending=False).head(num_games)
    results = []

    for _, row in team_games.iterrows():
        if row['HomeTeam'] == team:
            opponent = row['AwayTeam']
            goals = f"{row['FTHG']} - {row['FTAG']}"
            result = "W" if row['FTR'] == "H" else "L" if row['FTR'] == "A" else "D"
        else:
            opponent = row['HomeTeam']
            goals = f"{row['FTAG']} - {row['FTHG']}"
            result = "W" if row['FTR'] == "A" else "L" if row['FTR'] == "H" else "D"

        results.append({"Vika": row['GW'], "Mótherji": opponent, "Staða": goals, "Úrslit": result})

    return pd.DataFrame(results)

import tempfile  # Make sure tempfile is imported
import matplotlib.pyplot as plt  # Make sure matplotlib is imported
import mplcursors  # Make sure mplcursors is imported

def server(input, output, session):
    # Stadiums map with GPS coordinates
    @output
    @render_plotly
    def stadiums_map():
        fig = px.scatter_mapbox(
            stadiums_df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Stadium",
            hover_data={"Team": True, "City": True, "Capacity": True},
            zoom=5,
            height=600
        )

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(title="Stadiums in Premier League (with GPS Coordinates)")

        return fig

    # Display score table in Stöðutafla tab with dropdown for last 5 games
    @reactive.Calc
    def filtered_league_table():
        return calculate_league_table(games_df, input.game_week())

    @output
    @render.table
    def score_table():
        league_table_df = filtered_league_table()
        display_df = league_table_df[['POS', 'Team', 'Played', 'W', 'D', 'L', '+/-', 'PTS']]
        return display_df

    # Display last N games (including current week) for the selected team
    @output
    @render.table
    def last_games_table():
        team = input.team_select()
        game_week = input.game_week()
        num_games = input.num_games()
        last_games_df = get_last_n_games(team, game_week, num_games)
        return last_games_df

    # Render the plot based on selection in "Færanýtni" tab
    @output
    @render_plotly
    def efficiency_plot():
        plot_choice = input.plot_choice()

        if plot_choice == "Goals vs. Minutes":
            filtered_df = player_stats_df[(player_stats_df['MIN'] > 0) & (player_stats_df['G'] > 0)]
            fig = px.scatter(filtered_df, x='MIN', y='G', hover_name='PLAYER', title="Goals vs. Minutes Played")

        elif plot_choice == "Shots on Target vs. Goals":
            filtered_df = player_stats_df[player_stats_df['SOG'] > 0]
            fig = px.scatter(filtered_df, x='SOG', y='G', hover_name='PLAYER', title="Shots on Target vs. Goals")

        elif plot_choice == "Top Goalscorers":
            top_n = input.top_n_scorers()
            top_scorers_df = player_stats_df[player_stats_df['G'] >= 1].nlargest(top_n, 'G')
            fig = px.bar(top_scorers_df, x='PLAYER', y='G', title="Top Goalscorers", labels={'G': 'Goals'})

        return fig

    # Calculate betting profit
    @reactive.Calc
    def calculate_betting_profit():
        team = input.bet_team_select()
        bet_amount = 10
        profit_data = []
        cumulative_profit = 0

        # Filter games where the selected team played
        team_games = games_df[(games_df['HomeTeam'] == team) | (games_df['AwayTeam'] == team)]

        # Calculate profit for each game week
        for _, game in team_games.iterrows():
            if game['HomeTeam'] == team:
                if game['FTR'] == 'H':  # Team won as home team
                    profit = (game['B365H'] * bet_amount) - bet_amount
                else:
                    profit = -bet_amount  # Loss if not a win
            else:  # Team played as away team
                if game['FTR'] == 'A':  # Team won as away team
                    profit = (game['B365A'] * bet_amount) - bet_amount
                else:
                    profit = -bet_amount  # Loss if not a win

            cumulative_profit += profit
            profit_data.append({"Week": game['GW'], "Profit/Loss": profit, "Cumulative Profit": cumulative_profit})

        return profit_data

   # Betting progress plot with hover and selectable week details
    @output
    @render.image
    def betting_progress_plot():
        profit_data = calculate_betting_profit()
        profit_over_time = [item["Cumulative Profit"] for item in profit_data]

        # Create a temporary file to save the plot
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.figure(figsize=(10, 5))

        # Separate positive and negative profits for different color lines
        x_values = range(len(profit_over_time))
        positive_profit = [p if p > 0 else None for p in profit_over_time]
        negative_profit = [p if p < 0 else None for p in profit_over_time]

        # Plot profit and loss with hover annotations
        line_positive, = plt.plot(x_values, positive_profit, marker='o', linestyle='-', linewidth=2, color='green', label='Profit')
        line_negative, = plt.plot(x_values, negative_profit, marker='o', linestyle='-', linewidth=2, color='red', label='Loss')

        # Add interactive hover annotations using mplcursors
        cursor = mplcursors.cursor([line_positive, line_negative], hover=True)
        cursor.connect(
            "add", lambda sel: sel.annotation.set_text(
                f"Week: {profit_data[sel.index]['Week']}\n"
                f"Profit/Loss: ${profit_data[sel.index]['Profit/Loss']:.2f}\n"
                f"Cumulative Profit: ${profit_data[sel.index]['Cumulative Profit']:.2f}"
            )
        )

        plt.title(f"Uppsafnaður hagnaður/tap fyrir {input.bet_team_select()} (Miðast við 10\\$ bet á sigur fyrir hvern leik; D/L = -10\\$)")
        plt.xlabel("Game Week")
        plt.ylabel("Cumulative Profit/Loss ($)")
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add a horizontal line at 0 for clarity
        plt.legend()  # Add a legend to differentiate profit and loss
        plt.tight_layout()
        plt.savefig(temp_file.name)  # Save the plot to the temp file
        plt.close()  # Close the plot to free memory

        return {"src": temp_file.name}  # Return the path to the temporary image file



    # Function to calculate and return end-of-season profit/loss
    @output
    @render.text
    def end_season_profit_loss():
        profit_data = calculate_betting_profit()
        end_season_profit = profit_data[-1]["Cumulative Profit"] if profit_data else 0
        color = "green" if end_season_profit > 0 else "red"
        return f"Hagnaður/tap í lok tímabils: ${end_season_profit:.2f}"



# Run the app
app = App(app_ui, server)