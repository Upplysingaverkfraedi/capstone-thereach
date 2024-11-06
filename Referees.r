library(DBI)
library(RSQLite)
library(ggplot2)

# Tengjast við SQLite gagnagrunnin
conn <- dbConnect(SQLite(), "C:/Users/erlen/OneDrive - Menntaský (1)/Annað ár (2024-2025)/Haustönn 2024/Upplýsingaverkfræði/premier_league.db")

# Keyra og savea í R
query <- "
SELECT 
    Referee,
    SUM(HF + AF) AS Total_Fouls,
    SUM(HY + AY) AS Total_Yellow_Cards,
    SUM(HR + AR) AS Total_Red_Cards
FROM 
    games
GROUP BY 
    Referee;
"
referee_data <- dbGetQuery(conn, query)

# Aftengja
dbDisconnect(conn)

# Reikna fjöldi spjalda per brot
referee_data$Total_Cards <- referee_data$Total_Yellow_Cards + referee_data$Total_Red_Cards
referee_data$Fouls_Per_Card <- referee_data$Total_Fouls / referee_data$Total_Cards

ggplot(referee_data, aes(x = reorder(Referee, -Fouls_Per_Card), y = Fouls_Per_Card)) +
    geom_bar(stat = "identity") +
    labs(title = "Brot á hvert spjald að meðaltali fyrir hvern og einn dómara",
         x = "Dómari",
         y = "Brot á hvert spjald") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

# install.packages("plotly")

library(RSQLite)
library(plotly)

# Tenkjast SQLite gagnagrunni
conn <- dbConnect(SQLite(), "C:/Users/erlen/OneDrive - Menntaský (1)/Annað ár (2024-2025)/Haustönn 2024/Upplýsingaverkfræði/premier_league.db")

# Nota SQL til að vinna með gögn um dómara
query <- "
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
    GROUP_CONCAT(DISTINCT mt.Team) AS Most_Officiated_Teams
FROM 
    games AS r
LEFT JOIN 
    Most_Officiated_Teams AS mt ON r.Referee = mt.Referee
GROUP BY 
    r.Referee
ORDER BY 
    r.Referee;
"

# Framkvæma niðurstöður
referee_data <- dbGetQuery(conn, query)

# Loka gagnagrunni
dbDisconnect(conn)

# Reikna total sigra
total_home_wins <- sum(referee_data$Total_Home_Team_Wins, na.rm = TRUE)
total_draws <- sum(referee_data$Total_Draws, na.rm = TRUE)
total_away_wins <- sum(referee_data$Total_Away_Team_Wins, na.rm = TRUE)

# Búa til pie chart
plot_ly(
    labels = c("Heima sigrar", "Jafntefli", "Úti sigrar"),
    values = c(total_home_wins, total_draws, total_away_wins),
    type = "pie",
    textinfo = "label+percent",
    insidetextorientation = "radial"
) %>% layout(title = "Dreifing á sigrum")

# Niðurhlaða libraries
library(DBI)
library(RSQLite)
library(dplyr)
library(ggplot2)
library(tidyverse)

# Tengjast SQLite gagangrunni
con <- dbConnect(RSQLite::SQLite(), "C:/Users/erlen/OneDrive - Menntaský (1)/Annað ár (2024-2025)/Haustönn 2024/Upplýsingaverkfræði/premier_league.db")

# Nota SQL til að vinna flesta sigra dæmda hjá liði
query <- "
SELECT Referee, WinningTeam, MAX(Wins) AS Wins FROM (
    SELECT Referee, 
           CASE WHEN FTR = 'H' THEN HomeTeam ELSE AwayTeam END AS WinningTeam, 
           COUNT(*) AS Wins
    FROM Games
    WHERE FTR IN ('H', 'A')
    GROUP BY Referee, WinningTeam
)
GROUP BY Referee
ORDER BY Wins DESC;
"

# Keyra og setja niðurstöður í DataFrame
referee_most_wins <- dbGetQuery(con, query)


# Prenta töflu
print(referee_most_wins)

# Plota gögn
ggplot(referee_most_wins, aes(x = Referee, y = Wins, fill = WinningTeam)) +
  geom_bar(stat = "identity") +
  labs(title = "Fjöldi sigra sem hver dómari dæmir fyrir lið",
       x = "Dómari", y = "Fjöldi sigra") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

dbDisconnect(con)

