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

# COVID TESTS PERFORMED
#df_csv = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv')

#keep_columns = ['Week', 'Aantal']

#df_data = df_csv[df_csv['Type'] == 'Totaal'][keep_columns]
#df_data = df_data.rename(columns={'Aantal': 'total_tests'})
#df_data = df_data.merge(df_csv[df_csv['Type'] == 'Positief'][keep_columns])
#df_data = df_data.rename(columns={'Aantal': 'positive_tests', 'Week': 'weeknum'})
#df_data = df_data.set_index(df_data['weeknum'])
#df_data = df_data.drop(columns='weeknum')
#df_data['percentage_positive'] = df_data.apply(lambda row: round(row['positive_tests'] / row['total_tests'] * 100, 2), axis=1)

#df_data.to_csv(output_path / 'tests_performed.csv')


from bs4 import BeautifulSoup
import requests

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

url = 'https://ggdghor.nl/nieuws/'
req = requests.get(url, headers)
soup = BeautifulSoup(req.content, 'html.parser')

urls = set()

for a in soup.find_all('a', href=True):
    if 'coronatests' in a['href']:
        urls.add(a['href'])

urls = list(urls)

import pandas as pd
import dateparser

df_tests = pd.read_html(urls[0], header=0)[0]
df_tests.columns = ['week', 'tests']

df_tests['tests'] = [int(t.replace('.', '')) for t in df_tests['tests']]
total = df_tests['tests'].iloc[-1]

df_tests = df_tests[:-1]  # remove totals row

df_tests['week'] = pd.to_datetime([dateparser.parse(d.lower().split('t/m')[1].strip()) for d in df_tests['week']]).week

df_tests.set_index('week', inplace=True)
df_tests.rename(columns={'tests': 'ggd-tests'}, inplace=True)

#df_tests.to_csv('ggd-tests.csv')

df_labs = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv')
df_labs = df_labs[df_labs['Type'] == 'Totaal']

df_labs = df_labs[['Week', 'Aantal']]
df_labs.rename(columns={'Week': 'week'}, inplace=True)

df_labs.set_index('week', inplace=True)
df_labs.rename(columns={'Aantal': 'labs-tests'}, inplace=True)

#df_labs.to_csv('labs-tests.csv')

df_merged = pd.DataFrame(index=df_tests.index.union(df_labs.index))
df_merged = df_merged.join(df_tests['ggd-tests'])
df_merged = df_merged.join(df_labs['labs-tests'])

df = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.json')

df['Date_of_publication'] = pd.to_datetime(df['Date_of_publication'])
df = df.set_index('Date_of_publication')

df_daily = df.resample('D').sum()

df_daily.rename(columns={'Total_reported': 'infected', 'Hospital_admission':  'hospitalized', 'Deceased': 'deceased'}, inplace=True)
df_daily.index.rename('date', inplace=True)
df_weekly = df_daily.resample('W-MON', label='left', closed='left').sum()  # label=left prevents off-by-one error in weeknum
df_weekly.index = df_weekly.index.week
df_weekly.index.rename('week', inplace=True)
#df_weekly.to_csv('weekly_from_municipality.csv')

df_pos = pd.DataFrame(index=df_merged.index)

df_calc = df_merged.join(df_weekly['infected'])
df_pos['pos_ggd'] = (df_calc['infected'] / df_calc['ggd-tests']).round(3)
df_pos['pos_labs'] = (df_calc['infected'] / df_calc['labs-tests']).round(3)

df_pos.join(df_labs).join(df_tests).join(df_weekly['infected']).to_csv('html/tests_performed.csv')

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
df_sewage.to_csv('html/sewage.csv', float_format='%.2g')


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
