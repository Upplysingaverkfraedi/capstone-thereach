from shiny import App, ui, render, reactive, req
import pandas as pd
import sqlite3

# Function to fetch data from SQLite
def fetch_referee_data():
    conn = sqlite3.connect("C:/Users/erlen/OneDrive - Menntaský (1)/Annað ár (2024-2025)/Haustönn 2024/Upplýsingaverkfræði/premier_league.db")
    query = """
    WITH Team_Count AS (
        SELECT 
            Referee,
            HomeTeam AS Team,
            COUNT(*) AS Games_Officiated
        FROM 
            games
        GROUP BY 
            Referee, HomeTeam
        UNION ALL
        SELECT 
            Referee,
            AwayTeam AS Team,
            COUNT(*) AS Games_Officiated
        FROM 
            games
        GROUP BY 
            Referee, AwayTeam
    ),
    Max_Games_Officiated AS (
        SELECT 
            Referee,
            MAX(Games_Officiated) AS Max_Games
        FROM 
            Team_Count
        GROUP BY 
            Referee
    ),
    Most_Officiated_Teams AS (
        SELECT 
            tc.Referee,
            tc.Team,
            tc.Games_Officiated
        FROM 
            Team_Count AS tc
        INNER JOIN 
            Max_Games_Officiated AS mgo
        ON 
            tc.Referee = mgo.Referee 
            AND tc.Games_Officiated = mgo.Max_Games
    )
    SELECT 
        r.Referee,
        COUNT(*) AS Total_Games,
        SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) AS Total_Home_Team_Wins,
        SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) AS Total_Draws,
        SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) AS Total_Away_Team_Wins,
        SUM(HY + AY) AS Total_Yellow_Cards,
        SUM(HR + AR) AS Total_Red_Cards,
        SUM(HF + AF) AS Total_Fouls_Committed,
        GROUP_CONCAT(DISTINCT mt.Team) AS Most_Officiated_Teams,
        mt.Games_Officiated AS Games_Officiated_for_Team
    FROM 
        games AS r
    LEFT JOIN 
        Most_Officiated_Teams AS mt ON r.Referee = mt.Referee
    GROUP BY 
        r.Referee
    ORDER BY 
        r.Referee;
    """
    referee_data = pd.read_sql_query(query, conn)
    conn.close()
    return referee_data

# Define UI layout
app_ui = ui.page_fluid(
    ui.h1("Tölfærði dómara"),
    ui.input_select("sort_by", "Sort by", choices=[
        "Total_Games", "Total_Home_Team_Wins", "Total_Draws", 
        "Total_Away_Team_Wins", "Total_Yellow_Cards", 
        "Total_Red_Cards", "Total_Fouls_Committed"
    ], selected="Total_Games"),
    ui.input_radio_buttons("sort_order", "Sort order", choices=["Ascending", "Descending"], selected="Descending"),
    ui.output_table("referee_table")
)

# Define server logic
def server(input, output, session):
    # Reactive expression to fetch and sort data
    @reactive.Calc
    def sorted_data():
        # Fetch data
        referee_data = fetch_referee_data()
        # Get sort parameters
        sort_by = input.sort_by()
        sort_order = input.sort_order()
        # Sort data
        referee_data = referee_data.sort_values(
            by=sort_by, 
            ascending=(sort_order == "Ascending")
        )
        return referee_data

    # Render the sorted table
    @output
    @render.table
    def referee_table():
        data = sorted_data()
        return data

# Create the Shiny app
app = App(app_ui, server)
