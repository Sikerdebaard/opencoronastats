# number of births

import pandas as pd
import cbsodata
import requests
from pathlib import Path

output_path = Path('./html/')

try:
    cbs_df = pd.DataFrame(cbsodata.get_data('83474NED'))

    by_year = {}
    by_month = {}

    for idx, row in cbs_df.iterrows():
        try:
            year, month = row['Perioden'].split(' ')
        except ValueError as e:
            continue
        
        if month not in by_month:
            by_month[month] = {}
        by_month[month][year] = row['LevendGeborenKinderen_2']
            
            
        if year not in by_year:
            by_year[year] = {}
        by_year[year][month] = row['LevendGeborenKinderen_2']

    df = pd.DataFrame.from_dict(by_year)

    import numpy as np, scipy.stats as st

    confidence = .95

    cis = []
    for idx, row in df.iterrows():
        vals = row.values[:-1][-10:]  # slice off latest year (2020) then take last 5 years
        #ci = st.t.interval(confidence, len(vals) - 1, loc=np.mean(vals), scale=st.sem(vals))
        #cis.append({'week': idx, f'ci_{confidence}_low': int(ci[0]), f'ci_{confidence}_high': int(ci[1])})
        cis.append({'week': idx, f'min': np.min(vals), f'max': np.max(vals)})

    df_out = pd.DataFrame(cis).set_index('week')
    df_out = df_out.merge(df[df.columns[-5:]], left_index=True, right_index=True)  # only take last 5 years for visualisation

    df_out.to_csv(output_path / 'births.csv', index_label='month')
except requests.exceptions.HTTPError as ex:
    if 'will be released at' in str(ex):
        print('Skipping births, a new table will be released soon')
    else:
        raise ex

