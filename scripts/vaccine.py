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


df_vaccinated = pd.read_csv('https://raw.githubusercontent.com/Sikerdebaard/netherlands-vaccinations-scraper/main/augmented/doses_administered_cumulative.csv', index_col=0)
df_vaccinated.index = pd.to_datetime(df_vaccinated.index)
df_vaccinated = df_vaccinated['estimated'].rename('total_vaccinations').resample('D').interpolate('linear').to_frame()

# manually adjust to new magical Hugo number
interpolate = df_vaccinated.loc['2021-01-30']['total_vaccinations'] - df_vaccinated.loc['2021-01-29']['total_vaccinations']

idx = pd.date_range('2021-01-18', '2021-01-30')
interpolatedays = idx.shape[0] + 1
df_interpolate = pd.DataFrame(columns=['total_vaccinations'], index=idx)
df_interpolate['total_vaccinations'] = interpolate // interpolatedays
df_interpolate = df_interpolate.iloc[:-1]

df_merged = df_vaccinated['total_vaccinations'].to_frame().copy()

df_merged[df_merged.index.isin(df_interpolate.index)] += df_interpolate.cumsum()
        
df_merged['total_vaccinations'] = df_merged['total_vaccinations'].interpolate('linear')
df_merged['total_vaccinations'] = df_merged['total_vaccinations'].astype(int)

df_diff = df_merged['total_vaccinations'].diff()

assert df_diff[df_diff < 0].shape[0] == 0  # make sure that the data is still cumulative

## ADD MANUAL REAL-WORLD DATAPOINTS ON PEOPLE FULLY VACCINATED ##

people_fully_vaccinated = [
    ('2021-01-31', 13_500),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-13500-medewerkers-acute-zorg-voor-de-2de-keer-gevaccineerd
    ('2021-02-01', 26_500),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-26500-tweede-vaccinaties-gezet
    ('2021-02-02', 34_000),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-34000-tweede-vaccinaties-gezet
    ('2021-02-03', 38_000),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-38000-tweede-vaccinaties-gezet-en-7000-huisartsen-gevaccineerd
    ('2021-02-04', 39_500),  # https://www.lnaz.nl/nieuws/ziekenhuizen-hebben-39500-tweede-vaccinaties-gezet
    ('2021-02-07', 66_409),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-02-14', 154_445),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-02-21', 218_713),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-02-28', 331_671),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-03-07', 411_935),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-03-14', 493_123),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-03-21', 605_491),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-03-28', 690_062),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-04-04', 806_424),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
# FAULY -> https://www.rivm.nl/nieuws/correctie-vaccinatiecijfers-totaal-aantal-prikken-naar-beneden-bijgesteld
# FAULTY    ('2021-04-11', 826_135),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
# FAULTY    ('2021-04-18', 943_197),  # https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
    ('2021-04-25', 8_883 + 1_111_391),  # janssen estimate dashboard json + https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma
]

df_realworld = pd.DataFrame(people_fully_vaccinated, columns=['date', 'people_fully_vaccinated'])
df_realworld.set_index('date', inplace=True)
df_realworld.index = pd.to_datetime(df_realworld.index)
df_realworld.sort_index(inplace=True)

interpolate = False
if interpolate:
    idx = pd.date_range('2021-01-27', df_realworld.index[-1])
    df_realworld = df_realworld.reindex(idx)
    df_realworld.at[df_realworld.index[0], 'people_fully_vaccinated'] = 0
    df_realworld['people_fully_vaccinated'] = df_realworld['people_fully_vaccinated'].interpolate('linear')

df_merged = df_merged.join(df_realworld)

## < /> MANUAL REAL WORLD POINTS ##



df_nl = df_merged.copy()


## DAILY DAILY ##

df_nl['daily_vaccinations'] = df_nl['total_vaccinations'].diff().fillna(0).astype(int)
df_nl['sma7_daily_vaccinations'] = df_nl['daily_vaccinations'].rolling(7).mean().round(0).fillna(0).astype(int)
df_nl['total_vaccinations_per_hundred'] = (df_nl['total_vaccinations'] / popsize * 100).round(2)

df_nl.to_csv('html/daily-vaccine-rollout.csv')

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
df_model = df_model.join(df_nl[['people_fully_vaccinated', 'total_vaccinations']])

df_model.to_csv('html/vaccinated-estimate-latest.csv')
