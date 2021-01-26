import pandas as pd
import cbsodata
from datetime import date
from pathlib import Path

cachestamp_week = date.today().strftime('%G-%V')
cbsfile = Path(f'cache/{cachestamp_week}-83474NED')

if cbsfile.exists():
    df_83474NED = pd.read_json(cbsfile)
else:
    df_83474NED = pd.DataFrame(cbsodata.get_data('83474NED'))
    df_83474NED.to_json(cbsfile)

popsize = df_83474NED.iloc[-1]['BevolkingAanHetEindVanDePeriode_8']


manual_points = [
        {
            'date': '2021-01-25',
            'total_vaccinations': 150_000,
            'people_vaccinated': 150_000,
            'total_vaccinations_per_hundred': 150_000 / popsize * 100,
            'people_vaccinated_per_hundred': 150_000 / popsize * 100
        },  # https://twitter.com/hugodejonge/status/1353722492972638208
        {
            'date': '2021-01-26',
            'total_vaccinations': 163_931,
            'people_vaccinated':  163_931,
            'total_vaccinations_per_hundred': 163_931 / popsize * 100,
            'people_vaccinated_per_hundred': 163_931 / popsize * 100
        },  # corona dashboard 
]


## DAILY DAILY ##


df_owid = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')

df_owid['date'] = pd.to_datetime(df_owid['date'])

df_nl = df_owid[df_owid['iso_code'] == 'NLD'].copy()

df_nl['date'] = pd.to_datetime(df_nl['date'])
df_nl = df_nl.set_index('date')
df_nl.sort_index(inplace=True)

df_nl = df_nl.ffill()

vaccinated = df_nl.iloc[-1]['total_vaccinations'].astype(int)

# insert 0 datapoint at beginning
if df_nl.iloc[0]['total_vaccinations'] != 0:
    idx = (df_nl.index[0] - pd.Timedelta(days=1))
    df_nl.loc[idx] = None
    df_nl.at[idx, 'location'] = 'Netherlands'
    df_nl.at[idx, 'iso_code'] = 'NLD'
    df_nl.at[idx, 'total_vaccinations'] = 0.0
    df_nl.at[idx, 'daily_vaccinations'] = 0.0
    df_nl.at[idx, 'total_vaccinations_per_hundred'] = 0
    df_nl.at[idx, 'daily_vaccinations_per_million'] = 0
    df_nl.at[idx, 'people_vaccinated_per_hundred'] = 0
             
    df_nl.sort_index(inplace=True)


for mep in manual_points:
    mep['date'] = pd.to_datetime(mep['date'])
    if mep['date'] not in df_nl.index:
        print(f'Appending manual datapoint {mep}')
        df_nl.loc[mep['date']] = {col: mep[col] if col in mep else None for col in df_nl.columns  }
        
df_nl.resample('D').last().ffill()
df_nl['daily_vaccinations_raw'] = df_nl['total_vaccinations'].diff()  # fix this column after ffill

df_nl['sma7_daily_vaccinations'] = df_nl['daily_vaccinations_raw'].rolling(7).mean().round(0)
    
df_nl.drop(columns=['location', 'iso_code']).to_csv('html/daily-vaccine-rollout.csv')

## < /> DAILY DAILY ##

## WEEKLY WEEKLY ##
df_weekly = df_nl.resample('W-MON', label='left', closed='left').agg({
    'total_vaccinations': 'max',
    'people_vaccinated': 'max',
    'people_fully_vaccinated': 'max',
    'daily_vaccinations_raw': 'mean',
    'total_vaccinations_per_hundred': 'max',
    'people_vaccinated_per_hundred': 'max',
    'people_fully_vaccinated_per_hundred': 'max',
    'daily_vaccinations_per_million': 'mean',
})
df_weekly.index = df_weekly.index.strftime('%G-%V')

df_weekly.to_csv('html/weekly-vaccine-rollout.csv')

## < /> WEEKLY WEEKLY ##


## COMPARISON COMPARISON ##
df_compare = df_owid.pivot_table(
    values=['people_vaccinated', 'people_fully_vaccinated', 'daily_vaccinations_raw', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred'],
    index='date',
    columns='iso_code',

)



df_compare.columns = df_compare.columns.to_series().str.join('_')

interest_in = ['BEL', 'DEU', 'FRA', 'DNK']  # BELGIUM, GERMANY, FRANCE, DENMARK
nldcol = 'people_vaccinated_per_hundred_NLD'

keep_cols = [x for x in df_compare.columns if 'people_vaccinated_per_hundred' in x and x.split('_')[-1] in interest_in]

df_compare = df_compare[keep_cols]

df_compare = df_compare.ffill().dropna(how='all')

df_compare.index = pd.to_datetime(df_compare.index)

idx = (df_compare.index[0] - pd.Timedelta(days=1))

df_compare.loc[idx] = None
df_compare.sort_index(inplace=True)

df_compare = df_compare.join(df_nl['people_vaccinated_per_hundred'].rename('people_vaccinated_per_hundred_NLD'))
df_compare[nldcol] = df_compare[nldcol].ffill()

df_compare.to_csv('html/compare-vaccine.csv')

## < /> COMPARE COMPARE ##
