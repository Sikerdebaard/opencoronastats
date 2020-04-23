#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pathlib import Path
import numpy as np

def join_xlsx(df, url, valid_cols, index_col=0, rename=False):
    df2 = clean_cols(pd.read_excel(url, index_col=index_col), valid_cols)

    if rename:
        df2.rename(rename, axis=1, inplace=True)

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


df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/intake-count.xlsx', index_col=0)
df.rename({'value': 'intakeCount'}, axis=1, inplace=True)
df['intakeCount'] = df['intakeCount'].astype(int)
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/died-and-survivors-cumulative.xlsx',
               ['died', 'survivors', 'moved'])
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/intake-cumulative.xlsx',
               ['value'], rename={'value': 'intakeCumulative'})
df = join_csv(df, 'data/beds.csv', ['beds'])
df['covid_beds'] = df['beds'] - 500
df['covid_beds'] = df['covid_beds'].clip(0)
df['beds'] = df['beds']

df['died'] = df['died'].fillna(0).astype(int)
df['survivors'] = df['survivors'].fillna(0).astype(int)
df['moved'] = df['moved'].fillna(0).astype(int)
df['intakeCumulative'] = df['intakeCumulative'].fillna(0).astype(int)

df['mortality_rate'] = df.apply(
    lambda row: float(row['died']) / row['intakeCumulative'] if row['intakeCumulative'] > 0 else np.NaN, axis=1)
df['mortality_rate'] = df['mortality_rate'].replace(0, np.NaN)

df = calc_growth(df, 'intakeCount')

df_lcps = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/lcps_ic.csv', index_col=0)
df_lcps.rename(columns={'Aantal': 'lcps_beds'}, inplace=True)

df = df.join(df_lcps)

output_path = Path('./html')

df.to_csv(output_path / 'data.csv', index_label='date')


# demographics

df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/age-distribution-status.xlsx', index_col=0)
#df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/age-distribution-died-and-survivors.xlsx', ['died', 'survived'])
df.to_csv(output_path / 'demographics.csv', index_label='age_group')


# alt demographics - recovery times
df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/behandelduur-distribution.xlsx', index_col=0)
df.to_csv(output_path / 'treatment_durations.csv', index_label='days_of_treatment')



