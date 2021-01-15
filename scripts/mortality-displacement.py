import cbsodata
import pandas as pd
import json
import re
import numpy as np
import datetime

from pathlib import Path


displacement_dfs = {}

cachedir = Path('cache')


def calcwrappedsma(vals, window_size=7):

    smavals = []
    for i in range(0, len(vals)):
        s = 0
        for j in range(i - int(np.floor(window_size / 2)), i + int(np.ceil(window_size / 2))):
            s += vals[j % len(vals)]
        smavals.append(round(s / window_size, 0))
        
    return smavals

def cbsmortalitydisplacement():
    cbstable = '70895ned'
    info = cbsodata.get_info(cbstable)
    
    modified = info['Modified']
    
    cachefile = cachedir / f"{modified.replace(':', '_')}-cbsmortdispl.json"
    
    if cachefile.exists():
        with open(cachefile) as fh:
            return json.load(fh)
        
    data = cbsodata.get_data(cbstable)
    
    with open(cachefile, 'w') as fh:
        json.dump(data, fh)

    
    return data


df_cbs = pd.DataFrame(cbsmortalitydisplacement()).set_index('ID')
df_cbs = df_cbs.loc[(df_cbs['Geslacht'] == 'Totaal mannen en vrouwen') & (df_cbs['LeeftijdOp31December'] == 'Totaal leeftijd')]

overleden_col = [s for s in df_cbs.columns if 'Overledenen' in s][0]

df_cbs = df_cbs[['Perioden', overleden_col]]

#lets do some filtering
df_cbs = df_cbs[df_cbs['Perioden'].str.contains('week')]
df_cbs['year'] = df_cbs['Perioden'].apply(lambda v: int(v.split(' ')[0]))
df_cbs['week'] = df_cbs['Perioden'].apply(lambda v: int(re.sub('[^0-9]','', v.split('(')[0].strip().split(' ')[-1])))

#we are only interested in these years for the stddev
range_start = 2015
range_end = 2019

use_years = list(range(range_start - 1, range_end + 1))  # use 2015 - 2019, 2020 is ignored due to the way range works, also add 2014 for potential border-weeks
df_statistics = df_cbs[df_cbs['year'].isin(use_years)]

df_statistics = df_statistics.pivot_table(index='week', columns='year', values=overleden_col)

# correct borderweeks using the CBS method
for col, val in df_statistics.loc[53].dropna().iteritems():   
    if col + 1 <= range_end:
        if np.isnan(df_statistics.at[0, col + 1]):
            df_statistics.at[1, col + 1] += val
        
# 2016 is a bit special
if 2016 in df_statistics.columns:
    df_statistics.at[52, 2016] += df_statistics.at[0, 2017]

df_statistics = df_statistics.drop(index=[0, 53])
df_statistics = df_statistics[[c for c in df_statistics.columns if c <=range_end and c >= range_start]]

mean = df_statistics.mean(axis=1).round(0)
stdev = df_statistics.std(axis=1).round(0)

df_statistics['mean'] = mean
df_statistics['std'] = stdev


        
df_statistics['mean_sma7'] = calcwrappedsma(mean.values, 7)
df_statistics['std_sma7'] = calcwrappedsma(stdev.values, 7)

#df_statistics['high'] = df_statistics['mean_sma7'] + 1.96 * 

df_statistics['mean_sma7'].sum()



# CBS prognosis mortality
# https://www.cbs.nl/nl-nl/maatwerk/2019/51/kernprognose-2019-2060
prognosis = {
    2020: 153402,
    2021: 155232,
}

calcforyear = 2020

seasonal_pattern = int(df_statistics['mean_sma7'].sum())

increase = {k: v / seasonal_pattern for k, v in prognosis.items()}

df_statistics['expected_seasonal_pattern'] = (df_statistics['mean_sma7'] * increase[calcforyear]).round(0)
df_statistics['expected_seasonal_pattern_high'] = (df_statistics['expected_seasonal_pattern'] + df_statistics['std_sma7'] * 1.96).round(0)  # 95% interval
df_statistics['expected_seasonal_pattern_low'] = (df_statistics['expected_seasonal_pattern'] - df_statistics['std_sma7'] * 1.96).round(0)  # 95% interval

df_statistics = df_statistics.astype(int)  # set everything in stone -> convert to int

# prepare 2020

df_2020 = df_cbs[df_cbs['year'] == 2020].pivot_table(index='week', columns='year', values=overleden_col)
df_2020.at[1, 2020] += df_cbs[(df_cbs['year'] == 2019) & (df_cbs['week'] == 53)][overleden_col].values[0]

df_2020

df_statistics = df_statistics.join(df_2020)

df_statistics['displacement_2020'] = df_statistics[2020] - df_statistics['expected_seasonal_pattern']
df_statistics['displacement_2020_high'] = df_statistics[2020] - df_statistics['expected_seasonal_pattern_low']
df_statistics['displacement_2020_low'] = df_statistics[2020] - df_statistics['expected_seasonal_pattern_high']

df_rivm = pd.read_csv(f'https://covid-analytics.nl/deceased.csv', index_col=0)

columns = ['rivm casereports', 'rivm municipality']
df_deceased = df_rivm[columns[0]].rename(columns[0].replace(' ', '_')).to_frame()

for col in columns[1:]:
    df_deceased[col.replace(' ', '_')] = df_rivm[col]

df_deceased = df_deceased[df_deceased.index.str.contains('2020')]
df_deceased.index = [int(i.split('-')[1]) for i in df_deceased.index]


df_statistics = df_statistics.join(df_deceased)
#df_statistics.to_csv(f'cache/mortality-displacement-.csv')

df_statistics

displacement_dfs[calcforyear] = df_statistics.copy()

df_statistics

df_cbs = pd.DataFrame(cbsmortalitydisplacement()).set_index('ID')
df_cbs = df_cbs.loc[(df_cbs['Geslacht'] == 'Totaal mannen en vrouwen') & (df_cbs['LeeftijdOp31December'] == 'Totaal leeftijd')]

overleden_col = [s for s in df_cbs.columns if 'Overledenen' in s][0]

df_cbs = df_cbs[['Perioden', overleden_col]]

#lets do some filtering
df_cbs = df_cbs[df_cbs['Perioden'].str.contains('week')]
df_cbs['year'] = df_cbs['Perioden'].apply(lambda v: int(v.split(' ')[0]))
df_cbs['week'] = df_cbs['Perioden'].apply(lambda v: int(re.sub('[^0-9]','', v.split('(')[0].strip().split(' ')[-1])))

#we are only interested in these years for the stddev
range_start = 2015
range_end = 2019

use_years = list(range(range_start - 1, range_end + 1))  # use 2015 - 2019, 2020 is ignored due to the way range works, also add 2014 for potential border-weeks
df_statistics = df_cbs[df_cbs['year'].isin(use_years)]

df_statistics = df_statistics.pivot_table(index='week', columns='year', values=overleden_col)

# correct borderweeks using the CBS method
for col, val in df_statistics.loc[53].dropna().iteritems():
    if col + 1 <= range_end:
        if np.isnan(df_statistics.at[0, col + 1]):
            df_statistics.at[1, col + 1] += val

# 2016 is a bit special
if 2016 in df_statistics.columns:
    df_statistics.at[52, 2016] += df_statistics.at[0, 2017]

df_statistics = df_statistics.drop(index=[0, 53])
df_statistics = df_statistics[[c for c in df_statistics.columns if c <=range_end and c >= range_start]]

mean = df_statistics.mean(axis=1).round(0)
stdev = df_statistics.std(axis=1).round(0)

df_statistics['mean'] = mean
df_statistics['std'] = stdev



df_statistics['mean_sma7'] = calcwrappedsma(mean.values, 7)
df_statistics['std_sma7'] = calcwrappedsma(stdev.values, 7)

#df_statistics['high'] = df_statistics['mean_sma7'] + 1.96 *

df_statistics['mean_sma7'].sum()


calcforyear = 2021

seasonal_pattern = int(df_statistics['mean_sma7'].sum())

df_statistics['expected_seasonal_pattern'] = (df_statistics['mean_sma7'] * increase[calcforyear]).round(0)
df_statistics['expected_seasonal_pattern_high'] = (df_statistics['expected_seasonal_pattern'] + df_statistics['std_sma7'] * 1.96).round(0)  # 95% interval
df_statistics['expected_seasonal_pattern_low'] = (df_statistics['expected_seasonal_pattern'] - df_statistics['std_sma7'] * 1.96).round(0)  # 95% interval

df_statistics = df_statistics.astype(int)  # set everything in stone -> convert to int

# prepare 2021

df_2021 = df_cbs[df_cbs['year'] == 2021].pivot_table(index='week', columns='year', values=overleden_col)
#df_2021.at[1, 2021] += df_cbs[(df_cbs['year'] == 2021) & (df_cbs['week'] == 53)][overleden_col].values[0]

df_2021

df_statistics = df_statistics.join(df_2021)

df_statistics[f'displacement_{calcforyear}'] = df_statistics[calcforyear] - df_statistics['expected_seasonal_pattern']
df_statistics[f'displacement_{calcforyear}_high'] = df_statistics[calcforyear] - df_statistics['expected_seasonal_pattern_low']
df_statistics[f'displacement_{calcforyear}_low'] = df_statistics[calcforyear] - df_statistics['expected_seasonal_pattern_high']

df_rivm = pd.read_csv(f'https://covid-analytics.nl/deceased.csv', index_col=0)

columns = ['rivm casereports', 'rivm municipality']
df_deceased = df_rivm[columns[0]].rename(columns[0].replace(' ', '_')).to_frame()

for col in columns[1:]:
    df_deceased[col.replace(' ', '_')] = df_rivm[col]

df_deceased = df_deceased[df_deceased.index.str.contains(str(calcforyear))]
df_deceased.index = [int(i.split('-')[1]) for i in df_deceased.index]


df_statistics = df_statistics.join(df_deceased)
#df_statistics.to_csv('html/mortality-displacement.csv')

df_statistics

displacement_dfs[calcforyear] = df_statistics.copy()

df_statistics

df_output = pd.DataFrame(columns=['pattern', 'expected_seasonal_pattern', 'expected_seasonal_pattern_high', 'expected_seasonal_pattern_low', f'displacement', f'displacement_high', f'displacement_low', 'rivm_casereports', 'rivm_municipality'])
for year in sorted(displacement_dfs.keys()):
    cols = [year, 'expected_seasonal_pattern', 'expected_seasonal_pattern_high', 'expected_seasonal_pattern_low', f'displacement_{year}', f'displacement_{year}_high', f'displacement_{year}_low', 'rivm_casereports', 'rivm_municipality']
    df_displacement = displacement_dfs[year][cols]
    df_displacement.index = df_displacement.apply(lambda r: f'{year}-{int(r.name):02}', axis=1)

    rename = {
        year: 'pattern',
        f'displacement_{year}': 'displacement',
        f'displacement_{year}_high': f'displacement_high',
        f'displacement_{year}_low': f'displacement_low',
    }

    df_displacement = df_displacement.rename(columns=rename)

    df_output = pd.concat([df_output, df_displacement])


# manually add week 2020-53 from CBS as it is a bit of a strange week
# sometimes cbs calculates with week 53, sometimes with week 0
# in any case, this year its both, and we need to sum 2020-53 and 2021-0 to get the right value
pattern = df_cbs[((df_cbs['year'] == 2020) & (df_cbs['week'] == 53)) | ((df_cbs['year'] == 2021) & (df_cbs['week'] == 0))]['Overledenen_1'].astype(int).sum()
expected = 3266
expected_low = 2906
expected_high = 3652
df_output.loc['2020-53'] = {
    'pattern': pattern,
    'expected_seasonal_pattern': expected,
    'expected_seasonal_pattern_high': expected_high,
    'expected_seasonal_pattern_low': expected_low,
    'displacement': pattern - expected,
    'displacement_high': pattern - expected_low,
    'displacement_low': pattern - expected_high,
    'rivm_casereports': df_rivm.at['2020-53', 'rivm casereports'],
    'rivm_municipality': df_rivm.at['2020-53', 'rivm municipality']
}

df_output = df_output.sort_index()
df_output.index.rename('year-week', inplace=True)
df_output = df_output.loc[:df_output['pattern'].last_valid_index()]
df_output.to_csv('html/mortality-displacement.csv')
