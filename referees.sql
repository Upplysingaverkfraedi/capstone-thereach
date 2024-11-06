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
    SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) AS Total_Wins,
    SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) AS Total_Draws,
    SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) AS Total_Losses,
    SUM(HY + AY) AS Total_Yellow_Cards,
    SUM(HR + AR) AS Total_Red_Cards,
    SUM(HF + AF) AS Total_Fouls_Committed,
    GROUP_CONCAT(DISTINCT mt.Team) AS Most_Officiated_Teams,
    mt.Games_Officiated AS Games_Officiated_for_Team

FROM 
    games as r
LEFT JOIN
    Most_Officiated_Teams AS mt ON r.Referee = mt.Referee
GROUP BY 
    r.Referee
ORDER BY 
    r.Referee;
