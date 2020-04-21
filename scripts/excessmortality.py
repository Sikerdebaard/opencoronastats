# mortality displacement

import pandas as pd
import cbsodata
import requests
from pathlib import Path

output_path = Path('./html/')

try:
    data = cbsodata.get_data('70895ned')
    df = pd.DataFrame(data).set_index('ID')

    df = df.loc[(df['Geslacht'] == 'Totaal mannen en vrouwen') & (df['LeeftijdOp31December'] == 'Totaal leeftijd')].drop(columns=['Geslacht', 'LeeftijdOp31December'])

    #flat_output = []
    output = {}
    for idx, row in df.iterrows():
        if 'week 0' in row['Perioden'] or 'week' not in row['Perioden']:
            continue

        sd = row['Perioden'].split('week')
        year = int(sd[0].strip().split(' ')[0])
        week = int(sd[1].strip().split(' ')[0])
        deaths = int(row['Overledenen_1'])

        if week == 53:
            continue # drop week 53 as it is a bit of an odd one

        if year not in output:
            output[year] = {}
        output[year] = {**output[year], **{f'{week}': deaths}}


    df = pd.DataFrame(output)

    import numpy as np, scipy.stats as st

    confidence = .95

    cis = []
    for idx, row in df.iterrows():
        vals = row.values[:-1][-10:]  # slice off latest year (2020) then take last 5 years
        ci = st.t.interval(confidence, len(vals) - 1, loc=np.mean(vals), scale=st.sem(vals))
        cis.append({'week': idx, f'ci_{confidence}_low': int(ci[0]), f'ci_{confidence}_high': int(ci[1])})

    df_out = pd.DataFrame(cis).set_index('week')
    df_out = df_out.merge(df[df.columns[-5:]], left_index=True, right_index=True)  # only take last 5 years for visualisation

    rivm_df = pd.read_csv('./html/rivm.csv', index_col='date')

    rivm_df = pd.DataFrame(rivm_df['deceased'].copy())
    rivm_df['week'] = pd.to_datetime(rivm_df.index.to_series()).dt.week

    deceased_by_weeknum = pd.DataFrame(rivm_df.groupby('week')['deceased'].sum())
    deceased_by_weeknum.rename(columns={'deceased': 'official_deceased'}, inplace=True)
    deceased_by_weeknum.drop(deceased_by_weeknum.tail(1).index, inplace=True)
    deceased_by_weeknum.replace(0, np.nan, inplace=True)

    deceased_by_weeknum.index = deceased_by_weeknum.index.map(str)

    df_out = df_out.join(deceased_by_weeknum)

    df_out['normalized_excess_mortality_low'] = df_out[2020] - df_out['ci_0.95_high']
    df_out['normalized_excess_mortality_high'] = df_out[2020] - df_out['ci_0.95_low']

    cols = df_out.columns.to_list()
    cols.insert(0, cols.pop(-1))
    cols.insert(0, cols.pop(-1))
    cols.insert(0, cols.pop(-1))
    df_out = df_out.reindex(columns=cols)

    df_out.drop('1', inplace=True)  # drop week 1 as that one is a bit of an odd one

    df_out.to_csv(output_path / 'mortality_displacement.csv', index_label='week')
except requests.exceptions.HTTPError as ex:
    if 'will be released at' in str(ex):
        print('Skipping excess mortality, a new table will be released soon')
    else:
        raise ex

