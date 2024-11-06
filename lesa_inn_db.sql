create table match_status (
    Name text not NULL,
    Played int,
    Wins int,
    Draws int,
    Losses int,
    GF int,
    GA int,
    GoalDiff int,
    Pts int,
    season int not null,
    status_type text not null, 
    PRIMARY KEY(Name, status_type, season)
)


