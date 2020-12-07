import requests
import pandas as pd
import zipfile
import json
from io import BytesIO
import datetime

dashboard_datablob = 'https://coronadashboard.rijksoverheid.nl/latest-data.zip'

r = requests.get(dashboard_datablob, stream=True)
z = zipfile.ZipFile(BytesIO(r.content))

with z.open('json/NL.json') as fh:
    nl = json.load(fh)

rows = []
for week in nl['ggd']['values']:
    rows.append({
        'year-week': datetime.datetime.fromtimestamp(int(week['week_end_unix'])).strftime('%Y-%U'),
        'tested_pos': week['infected'],
        'tested_total': week['tested_total'],
        'percent_pos': week['infected_percentage'],
    })
    
df_ggd = pd.DataFrame(rows).set_index('year-week')


df_labs = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv')
df_labs = df_labs[df_labs['Type'] == 'Totaal']

df_labs['year-week'] = df_labs.apply(lambda r: f"{r['Jaar']}-{r['Week']}", axis=1)

df_labs = df_labs[['year-week', 'Aantal']]

df_labs.set_index('year-week', inplace=True)
df_labs.rename(columns={'Aantal': 'labs-tests'}, inplace=True)

df_merged = pd.merge(df_labs, df_ggd, how='outer', left_index=True, right_index=True)

print(df_merged)

df_merged.to_csv('html/tests_performed.csv')
