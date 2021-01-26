from pathlib import Path
import pandas as pd

output_path = Path('./html/')


def calc_growth(df, column):
    df[f'growth_{column}'] = df[column].pct_change()
    df[f'sma7_growth_{column}'] = df[f'growth_{column}'].rolling(window=7).mean()

    return df


#df = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/rivm_NL_covid19_national_by_date/rivm_NL_covid19_national_by_date_latest.csv')

#transformed_data = {}
#for idx, row in df.iterrows():
#    if row['Datum'] not in transformed_data:
#        transformed_data[row['Datum']] = {}
#    #transformed_data[row['Datum']][f'Labs'] = row['Labs']
#    transformed_data[row['Datum']][f'{row["Type"]}'] = row['Aantal']
#
#df_transformed = pd.DataFrame.from_dict(transformed_data, orient='index')
#df_transformed.rename(
#    columns={'Totaal': 'infected', 'Ziekenhuisopname': 'hospitalized', 'Overleden': 'deceased'},
#    inplace=True)

# df_transformed.to_csv(output_path / 'tests.csv', index_label='date')

#df_rivmnums = df_transformed.copy()

# df_rivmnums = calc_growth(df_rivmnums, 'infected')
# df_rivmnums = calc_growth(df_rivmnums, 'hospitalized')
# df_rivmnums = calc_growth(df_rivmnums, 'deceased')

df = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.json')

df['Date_of_report'] = pd.to_datetime(df['Date_of_report'])
df = df.set_index('Date_of_report')

df_daily = df.resample('D').sum().diff()
df_daily = df_daily.iloc[1:]

for col in df_daily.columns:
    df_daily[col] = df_daily[col].astype(int)
    
df_daily.rename(columns={'Total_reported': 'infected', 'Hospital_admission':  'hospitalized', 'Deceased': 'deceased'}, inplace=True)
df_daily.index.rename('date', inplace=True)

df_rivmnums = df_daily


# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

#  df_tests = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/rivm_NL_covid19_tests.csv')
#  
#  transformed_data = {}
#  for idx, row in df_tests.iterrows():
#      if row['Datum'] not in transformed_data:
#          transformed_data[row['Datum']] = {}
#      transformed_data[row['Datum']][f'Labs'] = row['Labs']
#      transformed_data[row['Datum']][f'{row["Type"]}'] = row['Aantal']
#  
#  df_transformed = pd.DataFrame.from_dict(transformed_data, orient='index')
#  df_transformed.rename(
#      columns={'Labs': 'labs_participating', 'Totaal': 'tests_cumulative', 'Positief': 'positive_tests_cumulative'},
#      inplace=True)
#  df_transformed['tests'] = df_transformed['tests_cumulative'].diff().fillna(0).astype(int)
#  df_transformed['positive_tests'] = df_transformed['positive_tests_cumulative'].diff().fillna(0).astype(int)
#  
#  df_out = df_rivmnums.join(df_transformed)

# this replaces above commented code
#df_out = df_rivmnums

# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

#df = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/rivm_NL_covid19_national.csv')

#transformed_data = {}
#for idx, row in df.iterrows():
#    if row['Datum'] not in transformed_data:
#        transformed_data[row['Datum']] = {}
#    transformed_data[row['Datum']][f'{row["Type"]}'] = row['Aantal']

#df_transformed = pd.DataFrame.from_dict(transformed_data, orient='index')
#df_transformed.rename(
#    columns={'Totaal': 'infected_cumulative', 'Ziekenhuisopname': 'hospitalized_cumulative', 'Overleden': 'deceased_cumulative'},
#    inplace=True)
#
#df_out = df_out.join(df_transformed)
#
#df_out.to_csv(output_path / 'rivm.csv', index_label='date')

df_daily_cum = df.resample('D').sum()
df_daily_cum = df_daily_cum.iloc[1:]
df_daily_cum.rename(columns={'Total_reported': 'infected_cumulative', 'Hospital_admission':  'hospitalized_cumulative', 'Deceased': 'deceased_cumulative'}, inplace=True)
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

df_sewage = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json')

df_sewage = df_sewage[df_sewage['Representative_measurement'] == True]

df_sewage['Date_measurement'] = pd.to_datetime(df_sewage['Date_measurement'])
df_sewage = df_sewage.set_index('Date_measurement')

df_sewage = pd.DataFrame(df_sewage['RNA_flow_per_100000'].resample('W-MON', label='left', closed='left').mean()).dropna()

if df_sewage.index[-1].week == pd.to_datetime(datetime.date.today()).week:
    print('Sewage: removing current week as it is incomplete')
    df_sewage = df_sewage[:-1]

df_sewage.index = df_sewage.index.format(formatter=lambda a: f'{a.year}-{a.week}')
df_sewage.index.rename('week', inplace=True)
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
