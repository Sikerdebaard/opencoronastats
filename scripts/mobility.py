import pandas as pd

mobility_df = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')

netherlands_df = mobility_df[mobility_df['country_region_code'] == 'NL']

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

df_result.to_csv('html/mobility.csv', index_label='date')