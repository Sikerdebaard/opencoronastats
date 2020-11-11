import pandas as pd

# GOOGLE

mobility_df = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')

#netherlands_df = mobility_df[mobility_df['country_region_code'] == 'NL']
netherlands_df = mobility_df[(mobility_df['country_region_code'] == 'NL') & (mobility_df['sub_region_2'].isnull())]

data = {}

for region in netherlands_df['sub_region_1'].unique():
    if pd.isnull(region):
        name = 'national'
        region_df = netherlands_df[netherlands_df['sub_region_1'].isnull()].copy()
    else:
        name = region
        region_df = netherlands_df[netherlands_df['sub_region_1'] == region].copy()

    for idx, row in region_df.iterrows():
        if row['date'] not in data:
            data[row['date']] = {}

        for col in region_df.columns:
            if 'from_baseline' in col:
                data[row['date']][f'{name.replace(" ", "_").lower()}_{col}'] = row[col]

df_result = pd.DataFrame.from_dict(data, orient='index')

df_result.to_csv('html/google-mobility.csv', index_label='date')



## APPLE

from functools import reduce
import requests

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

url = 'https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v3/index.json'
req = requests.get(url, headers)
json_data = req.json()

url = "https://covid19-static.cdn-apple.com" + json_data['basePath'] + json_data['regions']['en-us']['csvPath']

df_apple = pd.read_csv(url)

df_apple_nl = df_apple[df_apple['region'] == 'Netherlands']

types = df_apple_nl['transportation_type'].values

dfs = []

for t in types:
    df = df_apple_nl[df_apple_nl['transportation_type'] == t]
    to_drop = [c for c in df.columns if not c[0].isdigit()]
    df = df.drop(columns=to_drop).melt().rename(columns={'variable': 'date', 'value': t})
    df[t] = df[t] - 100
    dfs.append(df)

df_transit = reduce(lambda x, y: pd.merge(x, y, on='date'), dfs)

df_transit.to_csv('html/apple-mobility.csv')
