from shiny import App, ui, render
import pandas as pd
import sqlite3
import plotly.express as px

# Function to fetch and calculate data from SQLite
def fetch_referee_data():
    conn = sqlite3.connect("C:/Users/erlen/OneDrive - Menntaský (1)/Annað ár (2024-2025)/Haustönn 2024/Upplýsingaverkfræði/premier_league.db")
    query = """
    SELECT 
        Referee,
        SUM(HF + AF) AS Total_Fouls,
        SUM(HY + AY) AS Total_Yellow_Cards,
        SUM(HR + AR) AS Total_Red_Cards
    FROM 
        games
    GROUP BY 
        Referee;
    """
    referee_data = pd.read_sql_query(query, conn)
    conn.close()
    
    # Calculate total cards and fouls per card ratio
    referee_data['Total_Cards'] = referee_data['Total_Yellow_Cards'] + referee_data['Total_Red_Cards']
    referee_data['Fouls_Per_Card'] = referee_data['Total_Fouls'] / referee_data['Total_Cards']
    
    return referee_data

# Define UI layout
app_ui = ui.page_fluid(
    ui.h1("Brot á hvert spjald að meðaltali fyrir hvern og einn dómara"),
    ui.output_plot("fouls_per_card_plot")
)

# Define server logic
def server(input, output, session):
    @output
    @render.plot
    def fouls_per_card_plot():
        referee_data = fetch_referee_data()
        # Sort by Fouls_Per_Card for ordered plotting
        referee_data = referee_data.sort_values(by='Fouls_Per_Card', ascending=False)
        
        # Create a bar plot
        fig = px.bar(
            referee_data,
            x='Referee',
            y='Fouls_Per_Card',
            title="Brot á hvert spjald að meðaltali fyrir hvern og einn dómara",
            labels={"Fouls_Per_Card": "Brot á hvert spjald", "Referee": "Dómari"},
        )
        fig.update_layout(xaxis_tickangle=-45, template="simple_white")
        return fig

# Create the Shiny app
app = App(app_ui, server)
