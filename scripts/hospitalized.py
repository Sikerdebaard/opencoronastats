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
    df[f'sma7_growth_{column}'] = df[f'growth_{column}'].rolling(window=7).mean()

    return df


df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/intake-count.xlsx', index_col=0)
df.rename({'value': 'intakeCount'}, axis=1, inplace=True)
df['intakeCount'] = df['intakeCount'].astype(int)
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/died-and-survivors-cumulative.xlsx',
               ['cumulative_deceased', 'cumulative_recovered'])
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/intake-cumulative.xlsx',
               ['value'], rename={'value': 'intakeCumulative'})


df['cumulative_deceased'] = df['cumulative_deceased'].fillna(0).astype(int)
df['cumulative_recovered'] = df['cumulative_recovered'].fillna(0).astype(int)
df['intakeCumulative'] = df['intakeCumulative'].fillna(0).astype(int)

df['mortality_rate'] = df.apply(
    lambda row: float(row['cumulative_deceased']) / row['intakeCumulative'] if row['intakeCumulative'] > 0 else np.NaN, axis=1)
df['mortality_rate'] = df['mortality_rate'].replace(0, np.NaN)

df = calc_growth(df, 'intakeCount')

df_lcps = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/lcps_clinic.csv', index_col=0)
df_lcps.rename(columns={'Aantal': 'lcps_beds'}, inplace=True)
#df_lcps.drop_duplicates(inplace=True)

df = df.join(df_lcps)

output_path = Path('./html')

df.to_csv(output_path / 'hospitalized.csv', index_label='date')


# demographics

df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/age-distribution-status.xlsx', index_col=0)
df.to_csv(output_path / 'hospital_demographics.csv', index_label='age_group')


# alt demographics - recovery times
df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/behandelduur-distribution.xlsx', index_col=0)
df.to_csv(output_path / 'hospital_treatment_durations.csv', index_label='days_of_treatment')



