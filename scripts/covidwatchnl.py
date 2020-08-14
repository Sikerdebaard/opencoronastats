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


