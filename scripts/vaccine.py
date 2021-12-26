import pandas as pd
import cbsodata
from datetime import date
from pathlib import Path
import numpy as np

cachestamp_week = date.today().strftime('%G-%V')
cbsfile = Path(f'cache/{cachestamp_week}-83474NED')

if cbsfile.exists():
    df_83474NED = pd.read_json(cbsfile)
else:
    df_83474NED = pd.DataFrame(cbsodata.get_data('83474NED'))
    df_83474NED.to_json(cbsfile)

popsize = df_83474NED.iloc[-1]['BevolkingAanHetEindVanDePeriode_8']


import pandas as pd
import cbsodata
from datetime import date
from pathlib import Path
import numpy as np


df_mzelst = pd.read_csv('https://raw.githubusercontent.com/mzelst/covid-19/master/data-rivm/vaccines-ecdc/vaccines_administered_nl.csv')
df_vaccinated = df_mzelst.copy()

df_vaccinated['date'] = df_vaccinated.index.map(lambda x: pd.to_datetime(f'{df_vaccinated.at[x, "year"].astype(int)}-{df_vaccinated.at[x, "week"].astype(int)}-7', format='%G-%V-%u'))
df_vaccinated.set_index('date', inplace=True)
df_vaccinated.sort_index(inplace=True)


df_vaccinated = df_vaccinated.groupby('date')['total_administered'].sum().rename('total_vaccinations')
df_vaccinated = df_vaccinated.cumsum()
df_vaccinated = df_vaccinated.resample('D').interpolate('linear').round(0).astype(int).to_frame()

df_merged = df_vaccinated['total_vaccinations'].to_frame().copy()


#df_merged[df_merged.index.isin(df_interpolate.index)] += df_interpolate.cumsum()
        
#df_merged['total_vaccinations'] = df_merged['total_vaccinations'].interpolate('linear')
df_merged['total_vaccinations'] = df_merged['total_vaccinations'].astype(int)
df_diff = df_merged['total_vaccinations'].diff()

assert df_diff[df_diff < 0].shape[0] == 0  # make sure that the data is still cumulative

## ADD MANUAL REAL-WORLD DATAPOINTS ON PEOPLE FULLY VACCINATED ##

#  people_fully_vaccinated = [
#      ('2021-01-31', 13_500),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-13500-medewerkers-acute-zorg-voor-de-2de-keer-gevaccineerd
#      ('2021-02-01', 26_500),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-26500-tweede-vaccinaties-gezet
#      ('2021-02-02', 34_000),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-34000-tweede-vaccinaties-gezet
#      ('2021-02-03', 38_000),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-38000-tweede-vaccinaties-gezet-en-7000-huisartsen-gevaccineerd
#      ('2021-02-04', 39_500),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-39500-tweede-vaccinaties-gezet
#      ('2021-02-07', 66_409),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-02-14', 154_445),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-02-21', 218_713),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-02-28', 331_671),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-03-07', 411_935),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-03-14', 493_123),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-03-21', 605_491),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-03-28', 690_062),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-04-04', 806_424),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#  # FAULY -> https://www.rivm.nl/nieuws/correctie-vaccinatiecijfers-totaal-aantal-prikken-naar-beneden-bijgesteld
#  # FAULTY    ('2021-04-11', 826_135),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#  # FAULTY    ('2021-04-18', 943_197),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-04-25', 8_883 + 1_111_391),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-05-02', 48_422 + 1_203_113),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-05-09', 95_466 + 1_471_268),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-05-16', 124_373 + 1_786_899),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-05-23', 142_069 + 2_304_562),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-05-30', 156_277 + 2_805_074),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-06-06', 166_141 + 217_994 + 3_401_840),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#      ('2021-06-13', 172_542 + 258_536 + 4_019_591),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
#  ]
#  
#  df_realworld = pd.DataFrame(people_fully_vaccinated, columns=['date', 'people_fully_vaccinated'])
#  df_realworld.set_index('date', inplace=True)
#  df_realworld.index = pd.to_datetime(df_realworld.index)
#  df_realworld.sort_index(inplace=True)


#  interpolate = False
#  if interpolate:
#      idx = pd.date_range('2021-01-27', df_realworld.index[-1])
#      df_realworld = df_realworld.reindex(idx)
#      df_realworld.at[df_realworld.index[0], 'people_fully_vaccinated'] = 0
#      df_realworld['people_fully_vaccinated'] = df_realworld['people_fully_vaccinated'].interpolate('linear')
#  
#  df_merged = df_merged.join(df_realworld)

## < /> MANUAL REAL WORLD POINTS ##

import requests


req = requests.get('https://coronadashboard.rijksoverheid.nl/json/NL.json')
req.raise_for_status()
req.json()['vaccine_coverage']['values']

df_rivm_vacc = pd.DataFrame.from_dict(req.json()['vaccine_coverage']['values'])
df_rivm_vacc.index = pd.to_datetime(df_rivm_vacc['date_end_unix'], unit='s').rename('date')
df_rivm_vacc.sort_index(inplace=True)

#cols = ['partially_vaccinated', 'fully_vaccinated', 'partially_or_fully_vaccinated']

df_merged = df_merged.join(df_rivm_vacc['partially_vaccinated'].rename('rivm_partially_vaccinated'))
df_merged = df_merged.join(df_rivm_vacc['partially_or_fully_vaccinated'].rename('rivm_partially_or_fully_vaccinated'))
df_merged = df_merged.join(df_rivm_vacc['fully_vaccinated'].rename('people_fully_vaccinated'))



df_nl = df_merged.copy()


## DAILY DAILY ##

df_nl['daily_vaccinations'] = df_nl['total_vaccinations'].diff().fillna(0).astype(int)
df_nl['sma7_daily_vaccinations'] = df_nl['daily_vaccinations'].rolling(7).mean().round(0).fillna(0).astype(int)
df_nl['total_vaccinations_per_hundred'] = (df_nl['total_vaccinations'] / popsize * 100).round(2)



## booster

df_booster1 = df_mzelst.copy() 

df_booster1['date'] = df_booster1.index.map(lambda x: pd.to_datetime(f'{df_booster1.at[x, "year"].astype(int)}-{df_booster1.at[x, "week"].astype(int)}-7', format='%G-%V-%u'))
df_booster1.set_index('date', inplace=True)
df_booster1.sort_index(inplace=True)

df_booster1 = df_booster1[df_booster1['dose_number'] == 3]

df_booster1 = df_booster1.groupby('date')['total_administered'].sum().rename('cumulative_number_of_booster1_shots')
df_booster1 = df_booster1.cumsum()
df_booster1 = df_booster1.resample('D').interpolate('linear').round(0).astype(int).to_frame()

startdate = df_booster1[df_booster1['cumulative_number_of_booster1_shots'] == 0].index[-1]
df_booster1 = df_booster1[df_booster1.index >= startdate]

df_booster1.sort_index(inplace=True)

df_boosters = df_booster1['cumulative_number_of_booster1_shots'].rename('people_booster1').to_frame()

df_diff_booster1 = df_booster1['cumulative_number_of_booster1_shots'].resample('D').last().interpolate('linear').diff().fillna(0).astype(int)

total_vaccinations_sans_boosters = df_nl.loc[df_diff_booster1.index]['total_vaccinations'] - df_diff_booster1

df_nl['total_vaccinations_sans_boosters'] = df_nl['total_vaccinations']
df_nl.loc[df_diff_booster1.index, 'total_vaccinations_sans_boosters'] = total_vaccinations_sans_boosters

diff_test = df_nl['total_vaccinations_sans_boosters'].diff()
if diff_test[diff_test < 0].shape[0] != 0:
    print('WARNING! diff-test failed')

df_nl = df_nl.join(df_booster1['cumulative_number_of_booster1_shots'].astype(pd.Int64Dtype()))

## / booster

df_nl.to_csv('html/daily-vaccine-rollout.csv')
df_vacc_model_data = df_nl['total_vaccinations_sans_boosters'].rename('total_vaccinations').to_frame()
df_vacc_model_data = df_vacc_model_data.join(df_nl[['people_fully_vaccinated']])
df_vacc_model_data = df_vacc_model_data.join(df_booster1['cumulative_number_of_booster1_shots'].rename('people_booster1'))

df_vacc_model_data.astype(pd.Int64Dtype()).to_csv('html/vaccine-model-nl-country-data.csv')

## < /> DAILY DAILY ##

## WEEKLY WEEKLY ##
df_weekly = df_nl.resample('W-MON', label='left', closed='left').agg({
    'total_vaccinations': 'max',
#    'people_vaccinated': 'max',
#    'people_fully_vaccinated': 'max',
#    'daily_vaccinations_raw': 'mean',
    'total_vaccinations_per_hundred': 'max',
#    'people_vaccinated_per_hundred': 'max',
#    'people_fully_vaccinated_per_hundred': 'max',
#    'daily_vaccinations_per_million': 'mean',
})
df_weekly.index = df_weekly.index.strftime('%G-%V')

df_weekly.to_csv('html/weekly-vaccine-rollout.csv')

## < /> WEEKLY WEEKLY ##


## COMPARISON COMPARISON ##


df_owid = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
df_owid['date'] = pd.to_datetime(df_owid['date'])
df_compare = df_owid.pivot_table(
    values=['total_vaccinations_per_hundred', 'daily_vaccinations'],
    index='date',
    columns='iso_code',
)

df_compare.sort_index(inplace=True)

df_compare.columns = df_compare.columns.to_series().str.join('_')

interest_in = ['BEL', 'DEU', 'FRA', 'DNK']  # BELGIUM, GERMANY, FRANCE, DENMARK
nldcol = 'total_vaccinations_per_hundred_NLD'

keep_cols = [x for x in df_compare.columns if 'total_vaccinations_per_hundred' in x and x.split('_')[-1] in interest_in]

df_compare = df_compare[keep_cols]

df_compare = df_compare.ffill().dropna(how='all')
df_compare = df_compare[df_compare.sum(axis=1) > 0]  # filter any rows that sum to <= 0

df_compare.index = pd.to_datetime(df_compare.index)

idx = (df_compare.index[0] - pd.Timedelta(days=1))

df_compare.loc[idx] = None
df_compare.sort_index(inplace=True)

df_compare = df_compare.join(df_nl['total_vaccinations_per_hundred'].rename('total_vaccinations_per_hundred_NLD'))
df_compare[nldcol] = df_compare[nldcol].ffill()

df_compare.to_csv('html/compare-vaccine.csv')

## < /> COMPARE COMPARE ##



## doses received vs administered
df_weekly = pd.read_csv('html/weekly-vaccine-rollout.csv', index_col=0)

#df_initial = pd.read_csv('data/non-dashboard-vaccine-deliveries.csv', index_col=0).sum(axis=1).cumsum().rename('total').to_frame()
df_deliveries = pd.read_csv('https://raw.githubusercontent.com/Sikerdebaard/netherlands-vaccinations-scraper/main/vaccine-dose-deliveries-by-manufacturer.csv', index_col=0)
df_deliveries = df_deliveries[[col for col in df_deliveries.columns if 'date_' not in col]]
#df_deliveries = df_deliveries[~df_deliveries.index.isin(df_initial.index)]
#df_initial = df_initial[~df_initial.index.isin(df_deliveries.index)]


#df_merged = pd.concat([df_initial, df_deliveries])
df_merged = df_deliveries.copy()
df_merged = df_merged.astype(pd.Int64Dtype()).rename(columns={'total': 'cumulative'})

df_merged = df_merged.astype(int)
df_merged.index.rename('year-week', inplace=True)

df_merged.to_csv('html/vaccine-deliveries.csv')

df_merged = df_merged.join(df_weekly['total_vaccinations'], how='left')
df_merged['total_vaccinations'] = df_merged['total_vaccinations'].fillna(0).astype(int)

df_merged = df_merged[df_merged.index <= df_merged[df_merged['total_vaccinations'] != 0].index[-1]]
df_merged = df_merged[['cumulative', 'total_vaccinations']]
df_merged.to_csv('html/vaccine-delivered-vs-administered.csv')



## model estimates
df_model = pd.read_csv('data/vaccine_estimate/vaccinated-estimate-latest.csv', index_col=0)
df_model.index = pd.to_datetime(df_model.index)
df_model = df_model.join(df_nl[['people_fully_vaccinated', 'rivm_partially_vaccinated', 'total_vaccinations']])

df_model = df_model.join(df_boosters.astype(pd.Int64Dtype()))

for booster_name in df_boosters.columns:
    colname = f'percentage_pop_{booster_name.split("_")[-1]}'
    df_model[colname] = (df_model[booster_name] / popsize * 100).round(2)
    df_model[colname] = df_model[colname].interpolate('linear').round(2)

df_model['percentage_pop_vaccinated_rivm'] = (df_model['people_fully_vaccinated'] / popsize * 100).round(2)

df_model['percentage_pop_vaccinated'] = (df_model['vaccinated'] / popsize * 100).round(2)
df_model['percentage_pop_vaccinated_min'] = (df_model['vaccinated_min'] / popsize * 100).round(2)
df_model['percentage_pop_vaccinated_max'] = (df_model['vaccinated_max'] / popsize * 100).round(2)

df_model['percentage_pop_fully_vaccinated'] = (df_model['fully_vaccinated'] / popsize * 100).round(2)
df_model['percentage_pop_fully_vaccinated_min'] = (df_model['fully_vaccinated_min'] / popsize * 100).round(2)
df_model['percentage_pop_fully_vaccinated_max'] = (df_model['fully_vaccinated_max'] / popsize * 100).round(2)

df_model['percentage_pop_partially_vaccinated'] = (df_model['single_dose_vaccinated'] / popsize * 100).round(2)
df_model['percentage_pop_partially_vaccinated_min'] = (df_model['single_dose_vaccinated_min'] / popsize * 100).round(2)
df_model['percentage_pop_partially_vaccinated_max'] = (df_model['single_dose_vaccinated_max'] / popsize * 100).round(2)

df_model.to_csv('html/vaccinated-estimate-latest.csv')


df_projection = pd.read_csv('data/vaccine_estimate/projections/latest-projection.csv', index_col=0)
df_projection.to_csv('html/latest-projection.csv')
