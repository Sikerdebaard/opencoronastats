#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pathlib import Path
import datetime, time
import json
import numpy as np
import requests

def join_xlsx(df, url, valid_cols, index_col=0):
    df2 = clean_cols(pd.read_excel(url, index_col=index_col), valid_cols)

    df = df.join(df2, how='outer')

    return df

def join_csv(df, url, valid_cols, index_col=0):
    df2 = clean_cols(pd.read_csv(url, index_col=index_col), valid_cols)

    df = df.join(df2, how='outer')

    return df


def clean_cols(df, valid_cols):
    if not (isinstance(valid_cols, list) or isinstance(valid_cols, tuple)):
        valid_cols = [valid_cols]

    for col in df.columns:
        if col not in valid_cols:
            df = df.drop(columns=col)

    return df


def calc_growth(df, column):
    df[f'growth_{column}'] = df[column].pct_change()
    df[f'sma5_growth_{column}'] = df[f'growth_{column}'].rolling(window=5).mean()

    return df


df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/ic-count.xlsx', index_col=0)
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/died-and-survivors-cumulative.xlsx',
               ['died', 'survivors'])
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/intake-cumulative.xlsx',
               ['intakeCumulative'])
df = join_csv(df, 'data/beds.csv', ['beds'])

df['died'] = df['died'].fillna(0).astype(int)
df['survivors'] = df['survivors'].fillna(0).astype(int)
df['intakeCumulative'] = df['intakeCumulative'].fillna(0).astype(int)

df['mortality_rate'] = df.apply(
    lambda row: row['died'] / row['intakeCumulative'] if row['intakeCumulative'] > 0 else np.NaN, axis=1)
df['mortality_rate'] = df['mortality_rate'].replace(0, np.NaN)

df = calc_growth(df, 'intakeCount')

output_path = Path('./html')

df.to_csv(output_path / 'data.csv', index_label='date')


# demographics

df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/age-distribution.xlsx', index_col=0)
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/age-distribution-died-and-survivors.xlsx', ['died', 'survived'])
df.to_csv(output_path / 'demographics.csv', index_label='age_group')


# mortality displacement

import cbsodata
try:
    data = cbsodata.get_data('70895ned')
    df = pd.DataFrame(data).set_index('ID')

    df = df.loc[(df['Geslacht'] == 'Totaal mannen en vrouwen') & (df['LeeftijdOp31December'] == 'Totaal leeftijd')].drop(columns=['Geslacht', 'LeeftijdOp31December'])

    #flat_output = []
    output = {}
    for idx, row in df.iterrows():
        if 'week 0' in row['Perioden'] or 'week' not in row['Perioden']:
            continue

        sd = row['Perioden'].split('week')
        year = int(sd[0].strip().split(' ')[0])
        week = int(sd[1].strip().split(' ')[0])
        deaths = int(row['Overledenen_1'])

        if week == 53:
            continue # skip for now

        if year not in output:
            output[year] = {}
        output[year] = {**output[year], **{f'{week}': deaths}}
        #flat_output.append({'year': year, 'week': week, 'deaths': deaths})


    df = pd.DataFrame(output)

    import numpy as np, scipy.stats as st

    confidence = .95

    cis = []
    for idx, row in df.iterrows():
        vals = row.values[:-1][-10:]  # slice off latest year (2020) then take last 5 years
        ci = st.t.interval(confidence, len(vals) - 1, loc=np.mean(vals), scale=st.sem(vals))
        cis.append({'week': idx, f'ci_{confidence}_low': int(ci[0]), f'ci_{confidence}_high': int(ci[1])})

    df_out = pd.DataFrame(cis).set_index('week')
    df_out = df_out.merge(df[df.columns[-5:]], left_index=True, right_index=True)  # only take last 5 years for visualisation

    df_out.drop('1', inplace=True)  # drop week 1 as that one is a bit of an odd one

    df_out.to_csv(output_path / 'mortality_displacement.csv', index_label='week')
except requests.exceptions.HTTPError as ex:
    if 'will be released at' in str(ex):
        print('Skipping excess mortality, a new table will be released soon')
    else:
        raise ex

with (output_path / 'timestamp.json').open('w') as fh:
    json.dump(datetime.datetime.now().astimezone().isoformat(), fh)


