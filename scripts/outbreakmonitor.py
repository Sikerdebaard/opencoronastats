import pandas as pd
import cbsodata

import pandas as pd


# df = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data/rivm_NL_covid19_hosp_municipality.csv', index_col=0)

# df

def check_if_cumulative(df_test):
    types = set(df_test['Type'])
    municipalities = set(df_test['Gemeentecode'])
    is_cumulative = True

    for t in types:
        for municipality in municipalities:
            df_tmp = df_test[(df_test['Type'] == t) & (df_test['Gemeentecode'] == municipality)]
            df_tmp.sort_index(inplace=True)
            cum_diff = df_tmp['AantalCumulatief'].diff().values

            if any(cum_diff < 0):
                print(df_tmp.values)
                is_cumulative = False

    return is_cumulative


def fix_cumulative_vals(df_fix):
    types = set(df_fix['Type'])
    municipalities = set(df_fix['Gemeentecode'])

    # counter = 0
    for t in types:
        for municipality in municipalities:
            df_tmp = df_fix[(df_fix['Type'] == t) & (df_fix['Gemeentecode'] == municipality)].copy()
            df_tmp.sort_index(inplace=True)
            cum_diff = df_tmp['AantalCumulatief'].diff().values

            if any(cum_diff < 0):  # RIVM made some changes
                df_tmp['AantalCumulatief'] = df_tmp['AantalCumulatief'].fillna(method='ffill')

                vals = df_tmp['AantalCumulatief'].values

                for i in reversed(range(1, len(vals))):
                    if vals[i] < vals[i - 1]:
                        vals[i - 1] = vals[i]

                df_fix.loc[(df_fix['Type'] == t) & (df_fix['Gemeentecode'] == municipality), 'AantalCumulatief'] = vals


df = pd.read_csv('https://github.com/J535D165/CoronaWatchNL/raw/master/data-geo/data-municipal/RIVM_NL_municipal.csv',
                 index_col=0)
df.index = pd.to_datetime(df.index)

fix_cumulative_vals(df)
print(check_if_cumulative(df))

df = df[df['Type'] == 'Ziekenhuisopname']


cbs_df = pd.DataFrame(cbsodata.get_data('70072NED'))

keep_cols = ['RegioS', 'Perioden', 'TotaleBevolking_1', 'Code_269', 'Naam_270']

cbs_df = cbs_df[cbs_df['KoppelvariabeleRegioCode_306'].notna()]  # remove the ones with nan, can't use those
cbs_df = cbs_df[cbs_df['KoppelvariabeleRegioCode_306'].str.startswith('GM')]

gem_cache = {}
def bevolkingsaantal_per_gemeente(cbs_df, gmcode):
    if gmcode in gem_cache:  # cache vals to speed up calculation
        return gem_cache[gmcode]

    df_results = cbs_df[cbs_df['KoppelvariabeleRegioCode_306'].str.contains(gmcode)]

    if len(df_results) > 0:
        df_results = df_results.sort_values(['Perioden'])
        retval = df_results.loc[df_results['TotaleBevolking_1'].last_valid_index()]['TotaleBevolking_1'].astype(int)
        gem_cache[gmcode] = retval
        return retval

    return None


def gmcode(code):
    return f'GM{code:04d}'


def detect_outbreak(df_to_be_diffed, topx=None):
    df_diff = df_to_be_diffed.copy()
    df_sma = df_to_be_diffed.copy()
    df_sma_day_to_day = df_to_be_diffed.copy()

    for column in df_to_be_diffed.columns:
        df_diff[column] = df_to_be_diffed[column].diff()
        df_sma_day_to_day[column] = df_to_be_diffed[column].diff().pct_change().rolling(window=3).mean()
        df_sma[column] = df_to_be_diffed[column].pct_change().rolling(window=3).mean()

    df_sma = df_sma.sort_values(df_sma.last_valid_index(), axis=1, ascending=False)
    df_sma_day_to_day = df_sma_day_to_day.sort_values(df_sma_day_to_day.last_valid_index(), axis=1, ascending=False)

    df_outbreak_monitor = df_to_be_diffed[df_sma.columns]
    df_outbreak_monitor_daily = df_to_be_diffed[df_sma_day_to_day.columns]

    if topx is not None:
        return df_outbreak_monitor[df_outbreak_monitor.columns[:topx]], df_diff[df_outbreak_monitor.columns[:topx]], df_outbreak_monitor_daily[df_outbreak_monitor_daily.columns[:topx]]
    return df_outbreak_monitor, df_diff, df_outbreak_monitor_daily



data = {}
data_absolute = {}
for idx, row in df.iterrows():
    if idx not in data:
        data[idx] = {}
        data_absolute[idx] = {}

    if int(row['Gemeentecode']) < 0:  # this should not happen
        continue

    code = gmcode(row['Gemeentecode'])

    #hospitalized = row['Aantal']
    hospitalized = row['AantalCumulatief']
    population_size = bevolkingsaantal_per_gemeente(cbs_df, code)

    normalized_aantal = hospitalized / population_size * 100_000  # normalize to 100.000
    data[idx][row['Gemeentenaam']] = normalized_aantal
    data_absolute[idx][row['Gemeentenaam']] = hospitalized



df_normalized_hospitalized = pd.DataFrame.from_dict(data, orient='index')
df_absolute_hospitalized = pd.DataFrame.from_dict(data_absolute, orient='index')

df_outbreak, df_daily, df_outbreak_day_to_day = detect_outbreak(df_normalized_hospitalized, 10)
#df_outbreak.to_csv('outbreak_monitor_rebased_100_000.csv', index_label='date')
df_absolute_hospitalized[df_outbreak.columns[:10]].dropna().to_csv('html/outbreak_monitor_cumulative.csv', index_label='date')
df_absolute_hospitalized[df_outbreak_day_to_day.columns[:10]].dropna().to_csv('html/outbreak_monitor_daily.csv', index_label='date')

#df_outbreak