from pathlib import Path
import pandas as pd

output_path = Path('./html/')


def calc_growth(df, column):
    df[f'growth_{column}'] = df[column].pct_change()
    df[f'sma5_growth_{column}'] = df[f'growth_{column}'].rolling(window=5).mean()

    return df


df = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/rivm_NL_covid19_national_by_date/rivm_NL_covid19_national_by_date_latest.csv')

transformed_data = {}
for idx, row in df.iterrows():
    if row['Datum'] not in transformed_data:
        transformed_data[row['Datum']] = {}
    #transformed_data[row['Datum']][f'Labs'] = row['Labs']
    transformed_data[row['Datum']][f'{row["Type"]}'] = row['Aantal']

df_transformed = pd.DataFrame.from_dict(transformed_data, orient='index')
df_transformed.rename(
    columns={'Totaal': 'infected', 'Ziekenhuisopname': 'hospitalized', 'Overleden': 'deceased'},
    inplace=True)

# df_transformed.to_csv(output_path / 'tests.csv', index_label='date')

df_rivmnums = df_transformed.copy()

# df_rivmnums = calc_growth(df_rivmnums, 'infected')
# df_rivmnums = calc_growth(df_rivmnums, 'hospitalized')
# df_rivmnums = calc_growth(df_rivmnums, 'deceased')

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
df_out = df_rivmnums

# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

df = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/rivm_NL_covid19_national.csv')

transformed_data = {}
for idx, row in df.iterrows():
    if row['Datum'] not in transformed_data:
        transformed_data[row['Datum']] = {}
    transformed_data[row['Datum']][f'{row["Type"]}'] = row['Aantal']

df_transformed = pd.DataFrame.from_dict(transformed_data, orient='index')
df_transformed.rename(
    columns={'Totaal': 'infected_cumulative', 'Ziekenhuisopname': 'hospitalized_cumulative', 'Overleden': 'deceased_cumulative'},
    inplace=True)

df_out = df_out.join(df_transformed)

df_out.to_csv(output_path / 'rivm.csv', index_label='date')



# COVID TESTS PERFORMED
df_csv = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv')

keep_columns = ['Week', 'Aantal']

df_data = df_csv[df_csv['Type'] == 'Totaal'][keep_columns]
df_data = df_data.rename(columns={'Aantal': 'total_tests'})
df_data = df_data.merge(df_csv[df_csv['Type'] == 'Positief'][keep_columns])
df_data = df_data.rename(columns={'Aantal': 'positive_tests', 'Week': 'weeknum'})
df_data = df_data.set_index(df_data['weeknum'])
df_data = df_data.drop(columns='weeknum')
df_data['percentage_positive'] = df_data.apply(lambda row: round(row['positive_tests'] / row['total_tests'] * 100, 2), axis=1)

df_data.to_csv(output_path / 'tests_performed.csv')



## INFECTIONS
# R0, #infected etc.

df_data = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-reproduction/RIVM_NL_reproduction_index.csv', index_col=0)

df = df_data[df_data['Type'] == 'Minimum'].drop(columns=['Type']).rename(columns={'Waarde': 'r_min'})

df['r_max'] = df_data[df_data['Type'] == 'Maximum']['Waarde']
df['r'] = df_data[df_data['Type'] == 'Reproductie index']['Waarde']

df_data = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-contagious/RIVM_NL_contagious_estimate.csv', index_col=0)


df['contagious_min'] = df_data[df_data['Type'] == 'Minimum']['Waarde']
df['contagious_max'] = df_data[df_data['Type'] == 'Maximum']['Waarde']
df['contagious'] = df_data[df_data['Type'] == 'Geschat aantal besmettelijke mensen']['Waarde']

df.to_csv(output_path / 'infection.csv')

df_data = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-sewage/RIVM_NL_sewage_counts.csv', index_col=0)

df_data.index = pd.to_datetime(df_data.index).week
df_data.index.rename('week', inplace=True)
df_data = df_data.drop(columns=['Type']).rename(columns={'Aantal': 'virusparticles_per_ml'})

df_data.to_csv(output_path / 'sewage.csv')


df = pd.read_excel('https://github.com/Sikerdebaard/dutchcovid19data/raw/master/data/hospitalized/new-intake.xlsx', index_col=0)

df = df.groupby([pd.Grouper(freq='W-MON')])['confirmed'].sum()
df.index = df.index.week
df.index.rename('week', inplace=True)

df = pd.DataFrame(df)

df.rename(columns={'confirmed': 'hospitalized_per_day'}, inplace=True)

df_sewage = pd.read_csv('sewage.csv', index_col=0)

df['virusparticles_per_ml'] = df_sewage['virusparticles_per_ml']

df.drop(df.tail(1).index,inplace=True)

df.to_csv(output_path / 'hospitalized_vs_sewage.csv')
