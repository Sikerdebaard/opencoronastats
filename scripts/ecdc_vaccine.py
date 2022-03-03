import pandas as pd
import cbsodata
from datetime import date
from pathlib import Path
import numpy as np
import dateparser

cachestamp_week = date.today().strftime('%G-%V')
cbsfile = Path(f'cache/{cachestamp_week}-83474NED')

if cbsfile.exists():
    df_83474NED = pd.read_json(cbsfile)
else:
    df_83474NED = pd.DataFrame(cbsodata.get_data('83474NED'))
    df_83474NED.to_json(cbsfile)

# sort records by 'Perioden' date to make sure we can locate the latest number
df_83474NED.index = df_83474NED['Perioden'].map(lambda x: dateparser.parse(x).strftime('%Y-%m-01'))
df_83474NED.sort_index(inplace=True)

# take the most recent pop num
popsize = df_83474NED.iloc[-1]['BevolkingAanHetEindVanDePeriode_8']


import pandas as pd
import numpy as np


df = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/vaccine_tracker/csv/data.csv')

print('ECDC vaccine csv cols:', df.columns.values)

# if this fails then ECDC changed something
assert set(df.columns) == set(['YearWeekISO', 'ReportingCountry', 'Denominator', 'NumberDosesReceived',
       'NumberDosesExported', 'FirstDose', 'FirstDoseRefused', 'SecondDose',
       'DoseAdditional1', 'UnknownDose', 'Region', 'TargetGroup', 'Vaccine',
       'Population'])

df_nl = df[df['ReportingCountry'] == 'NL']
df_nl.index = df_nl['YearWeekISO'].map(lambda x: '-'.join(x.split('-W'))).rename('YearWeek')

# conversion from 1st/2nd/3th/xth dose to vaccinated / fully vaccinated / boosted

# NL reports Janssen as first dose, but we need to convert it to fully vaccinated
# if this assertion falses then this might no longer be true, or perhaps
# this vaccine is used as a booster
assert df_nl[df_nl['Vaccine'] == 'JANSS']['SecondDose'].sum() == 0


single_dose_vaccines = ['JANSS']

df_nl_flat = df_nl[~df_nl['Vaccine'].isin(single_dose_vaccines)].groupby('YearWeek')[['FirstDose', 'SecondDose', 'DoseAdditional1']].sum()
df_nl_flat['SecondDose'] += df_nl[df_nl['Vaccine'].isin(single_dose_vaccines)].groupby('YearWeek')['FirstDose'].sum()

# if this assert fails then ECDC changed something
assert (df_nl.groupby('YearWeek')[['FirstDose', 'SecondDose', 'DoseAdditional1']].sum().sum(axis=1).sort_index() == df_nl_flat.sum(axis=1)).all()

df_nl_flat['total_doses_administered'] = df_nl_flat.sum(axis=1)

doses_per_week = df_nl_flat.sum(axis=1)

df_nl_flat = df_nl_flat.sort_index().cumsum().rename(columns={
    'FirstDose': 'people_vaccinated',
    'SecondDose': 'people_fully_vaccinated',
    'DoseAdditional1': 'people_dose_additional1',
})


for col in df_nl_flat.columns:
    last_idx_zero = df_nl_flat.index[df_nl_flat[col] == 0][-1]
    df_nl_flat[col].replace(0, np.nan, inplace=True)
    df_nl_flat.at[last_idx_zero, col] = 0
    df_nl_flat[col] = df_nl_flat[col].astype(pd.Int64Dtype())

df_nl_flat = df_nl_flat.join(doses_per_week.sort_index().rename('doses_per_week'))

perc_pop_cols = {
    'people_vaccinated': 'percentage_population_vaccinated',
    'people_fully_vaccinated': 'percentage_population_fully_vaccinated',
    'people_dose_additional1': 'percentage_population_dose_additional1',
}
    
for k, v in perc_pop_cols.items():
    df_nl_flat[v] = (df_nl_flat[k] / popsize * 100).round(2)

df_nl_flat.to_csv('html/ecdc_vacc.csv')
