from rivmproxy import rivm_url
from pathlib import Path
import pandas as pd

output_path = Path('./html/')


def calc_growth(df, column):
    df[f'growth_{column}'] = df[column].pct_change()
    df[f'sma7_growth_{column}'] = df[f'growth_{column}'].rolling(window=7).mean()

    return df


df = pd.read_json(rivm_url('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.json'))
df
df['Date_of_publication'] = pd.to_datetime(df['Date_of_publication'])
df = df.set_index('Date_of_publication')

df_daily = df.resample('D').sum()
df_daily = df_daily.iloc[1:]

for col in df_daily.columns:
    df_daily[col] = df_daily[col].astype(int)
    
df_daily.rename(columns={'Total_reported': 'infected', 'Deceased': 'deceased'}, inplace=True)
df_daily.index.rename('date', inplace=True)

df_rivmnums = df_daily



df_daily_cum = df.resample('D').sum().cumsum()
df_daily_cum = df_daily_cum.iloc[1:]
df_daily_cum.rename(columns={'Total_reported': 'infected_cumulative', 'Deceased': 'deceased_cumulative'}, inplace=True)
df_daily_cum.drop(columns='Version', inplace=True)
df_rivmnums = df_rivmnums.join(df_daily_cum)


df_out = df_rivmnums
df_out.to_csv(output_path / 'rivm.csv', index_label='date')

## INFECTIONS
#df_data = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-sewage/RIVM_NL_sewage_counts.csv', index_col=0)

#df_data.index = pd.to_datetime(df_data.index).week
#df_data.index.rename('week', inplace=True)
#df_data = df_data.drop(columns=['Type']).rename(columns={'Aantal': 'virusparticles_per_ml'})

#df_data.to_csv(output_path / 'sewage.csv')

import datetime
import numpy as np

df_sewage = pd.read_json(rivm_url('https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json'))

df_sewage['Date_measurement'] = pd.to_datetime(df_sewage['Date_measurement'])
df_sewage = df_sewage.set_index('Date_measurement')

df_sewage.sort_index(inplace=True)
df_sewage['RNA_flow_per_100000'] = df_sewage['RNA_flow_per_100000'].replace('', np.nan).astype(float)
df_sewage = pd.DataFrame(df_sewage['RNA_flow_per_100000'].resample('W-MON', label='left', closed='left').mean()).dropna()

thisweek = pd.to_datetime(datetime.date.today()).strftime('%G-%V')

df_sewage.index = df_sewage.index.strftime('%G-%V')
df_sewage.index.rename('week', inplace=True)


df_sewage = df_sewage[df_sewage.index <= thisweek]

df_sewage.to_csv('html/sewage.csv', float_format='%.3g')


#df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/new-intake.xlsx', index_col=0)
#
#df.index = pd.to_datetime(df.index)
#df.index = df.index.rename('date')
#
#df = df.resample('W-Mon', label='left').sum()
#
#df = df.drop(columns={'not-confirmed'})
#
##df = df.groupby([pd.Grouper(freq='W-MON')])['confirmed'].sum()
#df.index = df.index.week
#df.index.rename('week', inplace=True)
#
#df = pd.DataFrame(df)
#
#df.rename(columns={'confirmed': 'hospitalized_per_day'}, inplace=True)
#
#df_sewage = pd.read_csv(output_path / 'sewage.csv', index_col=0)
#
#df['virusparticles_per_ml'] = df_sewage['virusparticles_per_ml']
#
#df.drop(df.tail(1).index,inplace=True)
#
#df.to_csv(output_path / 'hospitalized_vs_sewage.csv')
