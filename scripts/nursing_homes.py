import pandas as pd

df_nursinghomes = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_verpleeghuizen.json')

df_national = df_nursinghomes.groupby('Date_of_statistic_reported').sum()
df_national.index = pd.to_datetime(df_national.index)
df_national = df_national[df_national.index.year != 1900]  # year == 1900 means the date of the statistic is unknown

df_national = df_national.drop(columns=['Total_new_infected_locations_reported'])

df_national = df_national.sort_index()

df_national.to_csv('html/nursing-homes.csv')
