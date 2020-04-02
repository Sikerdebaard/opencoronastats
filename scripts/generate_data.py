#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pathlib import Path
import datetime, time
import json
import numpy as np


def join_xlsx(df, url, valid_cols, index_col=0):
    df2 = clean_cols(pd.read_excel(url, index_col=index_col), valid_cols)

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
df = join_xlsx(df,
               'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/died-and-survivors-cumulative.xlsx',
               ['died', 'survivors'])
df = join_xlsx(df, 'https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/intake-cumulative.xlsx',
               ['intakeCumulative'])

df['died'] = df['died'].fillna(0).astype(int)
df['survivors'] = df['survivors'].fillna(0).astype(int)
df['intakeCumulative'] = df['intakeCumulative'].fillna(0).astype(int)

df['mortality_rate'] = df.apply(
    lambda row: row['died'] / row['intakeCumulative'] if row['intakeCumulative'] > 0 else np.NaN, axis=1)
df['mortality_rate'] = df['mortality_rate'].replace(0, np.NaN)

df = calc_growth(df, 'intakeCount')

output_path = Path('./html')

df.to_csv(output_path / 'data.csv', index_label='date')

with (output_path / 'timestamp.json').open('w') as fh:
    json.dump(datetime.datetime.now().astimezone().isoformat(), fh)


