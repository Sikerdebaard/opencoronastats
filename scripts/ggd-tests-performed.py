import requests
import pandas as pd
import json
import datetime


nl = requests.get('https://coronadashboard.rijksoverheid.nl/json/NL.json').json()
data = nl['tested_ggd_daily']['values']


rows = []
for week in nl['tested_ggd_average']['values']:
    rows.append({
        'year-week': datetime.datetime.fromtimestamp(int(week['date_start_unix'])),
        'tested_pos': week['infected'],
        'tested_total': week['tested_total'],
        'percent_pos': week['infected_percentage'],
    })

df_ggd = pd.DataFrame(rows).set_index('year-week')


df_ggd = df_ggd.resample('W-MON', label='left', closed='left').agg({'tested_pos': 'sum', 'tested_total': 'sum', 'percent_pos': 'mean'})
df_ggd['percent_pos'] = df_ggd['percent_pos'].round(2)
df_ggd.index = df_ggd.index.strftime('%Y-%U')


df_labs = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv')
df_labs = df_labs[df_labs['Type'] == 'Totaal']

df_labs['year-week'] = df_labs.apply(lambda r: f"{r['Jaar']}-{r['Week']}", axis=1)

df_labs = df_labs[['year-week', 'Aantal']]

df_labs.set_index('year-week', inplace=True)
df_labs.rename(columns={'Aantal': 'labs-tests'}, inplace=True)

df_merged = pd.merge(df_labs, df_ggd, how='outer', left_index=True, right_index=True)

print(df_merged)

df_merged.to_csv('html/tests_performed.csv')


## DAILY DAILY DAILY ##
## DAILY DAILY DAILY ##
## DAILY DAILY DAILY ##
## DAILY DAILY DAILY ##

df = pd.DataFrame.from_dict(data)
df = df.set_index('date_unix')
df.index = df.index.rename('date')
df.index = pd.to_datetime(df.index, unit='s')
df = df.drop(columns='date_of_insertion_unix')

df['sma7_infected_percentage'] = df['infected_percentage'].rolling(7).mean()
df['sma7_infected_percentage'] = df['sma7_infected_percentage'].round(2)

df.to_csv('html/daily-tests-performed.csv')
