import pandas as pd

## DAILY DAILY ##


df_owid = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')

df_owid['date'] = pd.to_datetime(df_owid['date'])

df_nl = df_owid[df_owid['iso_code'] == 'NLD'].copy()

df_nl['date'] = pd.to_datetime(df_nl['date'])
df_nl = df_nl.set_index('date')
df_nl.sort_index(inplace=True)

df_nl = df_nl.ffill()
df_nl['daily_vaccinations_raw'] = df_nl['total_vaccinations'].diff()  # fix this column after ffill

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

interest_in = ['BEL', 'DEU', 'NLD', 'FRA', 'DNK']  # BELGIUM, GERMANY, NETHERLANDS, FRANCE, DENMARK
keep_cols = [x for x in df_compare.columns if 'people_vaccinated_per_hundred' in x and x.split('_')[-1] in interest_in]

df_compare = df_compare[keep_cols]

df_compare = df_compare.ffill().dropna(how='all')

df_compare.index = pd.to_datetime(df_compare.index)

idx = (df_compare.index[0] - pd.Timedelta(days=1))

df_compare.loc[idx] = None
df_compare.sort_index(inplace=True)

df_compare.to_csv('html/compare-vaccine.csv')

## < /> COMPARE COMPARE ##
