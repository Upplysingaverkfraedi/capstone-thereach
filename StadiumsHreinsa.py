import sqlite3
import re

# Tengjast gagnagrunn breyta file path eftir því hvar gagnagrunnurinn er staðsettur í þinni tölvu
db_path = '/Users/ingvaratliaudunarson/Documents/GitHub/capstone-thereach/premier_league.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Búa til regex segð sem leitar af liðum í Prem 2019/20
team_pattern = re.compile(r'\b(?:Liverpool|Manchester City|Manchester United|Chelsea|Leicester City|'
                          r'Tottenham Hotspur|Wolverhampton Wanderers|Arsenal|Sheffield United|'
                          r'Burnley|Southampton|Everton|Newcastle United|Crystal Palace|'
                          r'Brighton & Hove Albion|West Ham United|Aston Villa|Bournemouth|'
                          r'Watford|Norwich City)\b')

# Sækja öll lið Stadiums töflu
cursor.execute("SELECT Team FROM Stadiums")
all_teams = cursor.fetchall()

# Finna hvaða lið á að deleta frá töflunni (út frá regex)
teams_to_keep = [team[0] for team in all_teams if team_pattern.match(team[0])]
teams_to_delete = [team[0] for team in all_teams if team[0] not in teams_to_keep]

# Eyða liðunum sem voru ekki í prem á gefnum tíma
for team in teams_to_delete:
    cursor.execute("DELETE FROM Stadiums WHERE Team = ?", (team,))

# Commita breytingum 
conn.commit()

# Bæta við bournemouth og Sheffield, vantaði þau upprunalega í gagnagrunninn
missing_teams = [
    ("Bournemouth", "Bournemouth", "Vitality Stadium", 11379, 50.734841, -1.839080, "England"),
    ("Sheffield United", "Sheffield", "Bramall Lane", 32050, 53.370499, -1.470928, "England")
]

for team in missing_teams:
    # Bæta við Stadiums ef liðin eru þar ekki núþegar
    cursor.execute("SELECT 1 FROM Stadiums WHERE Team = ?", (team[0],))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO Stadiums (Team, City, Stadium, Capacity, Latitude, Longitude, Country)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, team)

# Commita breytingum
conn.commit()

# Loka tengingu
conn.close()
