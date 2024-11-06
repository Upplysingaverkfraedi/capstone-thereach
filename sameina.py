import pandas as pd

df1 = pd.read_csv('Games_season19-20.csv')
df2 = pd.read_csv('Premier League Player Stats.csv')

combined_df = pd.concat([df1, df2], axis=1)

combined_df.to_csv('combined_file.csv', index=False)