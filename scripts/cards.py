import pandas as pd
from math import log
import json
from pathlib import Path
import numpy as np
import decimal
from babel.numbers import format_decimal
import math

def fnum(x, decimals=None):
        if math.isinf(x):
            return '∞'

        if decimals is None:
            return format_decimal(x, locale="nl_NL")
        else:
            return format_decimal(round(x, decimals), locale="nl_NL", decimal_quantization=False)

def round(num, decimals=2):  # use old python 2 rounding
    return float(decimal.Decimal(num).quantize(decimal.Decimal(f'0.{"0" * decimals}'), rounding=decimal.ROUND_HALF_EVEN))

cards = {}

df_data = pd.read_csv('html/data.csv')

# -- growth

growth = df_data['sma7_growth_intakeCount'].tail(5).values[0:2]

if growth[0] == growth[1]:
    trend = 0
elif growth[0] > growth[1]:
    trend = -1
else:
    trend = 1

cards['icu-growth'] = {
    'trend': trend,
    'value': fnum(round(growth[1] * 100), 2),
    'title': 'Growth rate',
    'color': 'green' if trend <= 0 else 'red'
}

# -- doubling rate / half life

growth = round(growth[1] * 100) 
growth_trend = cards['icu-growth']['trend']
if growth < 0:  # half-life
    value = int(log(1 / 2) / log(1 + growth / 100))
    title = 'half life'

    if growth_trend == -1:
        trend = -1
        color = 'green'
    else:
        trend = 1
        color = 'red'
else:
    value = int(log(2) / log(1 + growth / 100))
    title = 'doubling rate'

    if growth_trend == 1:
        trend = 1
        color = 'green'
    else:
        trend = -1
        color = 'red'

cards['doubling-rate'] = {
    'trend': trend,
    'value': fnum(value),
    'title': title,
    'color': color
}

# -- patients recovered / deceased / beds

cards['patients-recovered-from-icu'] = {
    'value': fnum(df_data['survivors'].tail(4).values[0]),
    'title': 'Patients discharged from ICU',
    'color': 'blue'
}

cards['patients-deceased-from-icu'] = {
    'value': fnum(df_data['died'].tail(4).values[0]),
    'title': 'Patients deceased in ICU',
    'color': 'blue'
}

cards['beds-used-in-icu'] = {
    'value': fnum(df_data['lcps_beds'].loc[df_data['lcps_beds'].last_valid_index()].astype(int)),
    'title': 'Beds used for COVID',
    'color': 'blue'

}

cfr = df_data['mortality_rate'].tail(5).values[0:2]
trend = 1 if cfr[0] < cfr[1] else -1
cards['cfr-icu'] = {
    'value': fnum(cfr[1] * 100, 2),
    'title': 'Case Fatality Rate in ICU',
    'color': 'red' if trend == 1 else 'green',
    'trend': trend

}


#-------------
# hospitalized
#-------------

df_data = pd.read_csv('html/hospitalized.csv')

# -- growth

growth = df_data['sma7_growth_intakeCount'].tail(5).values[0:2]

if growth[0] == growth[1]:
    trend = 0
elif growth[0] > growth[1]:
    trend = -1
else:
    trend = 1

cards['hospitalized-growth'] = {
    'trend': trend,
    'value': fnum(round(growth[1] * 100)),
    'title': 'Growth rate',
    'color': 'green' if trend <= 0 else 'red'
}

# -- doubling rate / half life

growth = round(growth[1] * 100)
growth_trend = cards['hospitalized-growth']['trend']
if growth < 0:  # half-life
    value = int(log(1 / 2) / log(1 + growth / 100))
    title = 'half life'

    if growth_trend == -1:
        trend = -1
        color = 'green'
    else:
        trend = 1
        color = 'red'
else:
    value = int(log(2) / log(1 + growth / 100))
    title = 'doubling rate'

    if growth_trend == 1:
        trend = 1
        color = 'green'
    else:
        trend = -1
        color = 'red'

cards['hospitalized-doubling-rate'] = {
    'trend': trend,
    'value': fnum(value),
    'title': title,
    'color': color
}

# -- patients recovered / deceased / beds

cards['patients-recovered-from-hospital'] = {
    'value': fnum(df_data['cumulative_recovered'].tail(4).values[0]),
    'title': 'Patients discharged from hospital',
    'color': 'blue'
}

cards['hospitalized-deceased'] = {
    'value': fnum(df_data['cumulative_deceased'].tail(4).values[0]),
    'title': 'Hospitalized patients deceased',
    'color': 'blue'
}

cfr = df_data['mortality_rate'].tail(5).values[0:2]
trend = 1 if cfr[0] < cfr[1] else -1
cards['cfr-hospitalized'] = {
    'value': fnum(cfr[1] * 100, 2),
    'title': 'Case Fatality Rate for hospitalized patients',
    'color': 'red' if trend == 1 else 'green',
    'trend': trend

}


# -- population

df_rivm = pd.read_csv('html/rivm.csv')

# cards['rivm-total-tests'] = {
#     'value': df_rivm['tests_cumulative'].loc[df_rivm['tests_cumulative'].last_valid_index()].astype(int),
#     'title': 'Total tests performed',
#     'color': 'blue'
# }
#
# cards['rivm-total-tests-positive'] = {
#     'value': df_rivm['positive_tests_cumulative'].loc[df_rivm['positive_tests_cumulative'].last_valid_index()].astype(int),
#     'title': 'Total positive tests',
#     'color': 'blue'
# }

cards['rivm-total-infected'] = {
    'value': fnum(df_rivm['infected_cumulative'].loc[df_rivm['infected_cumulative'].last_valid_index()].astype(int)),
    'title': 'Total confirmed infected',
    'color': 'blue'
}

df_hospitalized_nice = pd.read_csv('html/hospitalized.csv', index_col=0)
df_hospitalized_nice.index = pd.to_datetime(df_hospitalized_nice.index)
df_hospitalized_nice.sort_index(inplace=True)
cards['nice-total-hospitalized'] = {
    'value': fnum(df_hospitalized_nice['intakeCumulative'].loc[df_hospitalized_nice['intakeCumulative'].last_valid_index()].astype(int)),
    'title': 'Total hospitalized',
    'color': 'blue'
}

cards['rivm-total-deceased'] = {
    'value': fnum(df_rivm['deceased_cumulative'].loc[df_rivm['deceased_cumulative'].last_valid_index()].astype(int)),
    'title': 'Total deceased',
    'color': 'blue'
}




# population infectious, reproduction-index etc.


df_data = pd.read_csv('html/infection.csv')

r = df_data['r'].loc[df_data['r'].last_valid_index()].astype(float)
contagious = df_data['contagious'].loc[df_data['contagious'].last_valid_index()].astype(int)

cards['rivm-r'] = {
    'value': fnum(r, 2),
    'title': 'Estimated reproduction index',
    'color': 'blue'
}

cards['rivm-contagious'] = {
    'value': fnum(contagious),
    'title': 'Estimated contagious people',
    'color': 'blue'
}




# nursing homes
df_national = pd.read_csv('html/nursing-homes.csv')

nursing_homes_reported_infected = df_national.loc[df_national.last_valid_index()]['Total_infected_locations_reported']

trend = 1 if df_national['Total_infected_locations_reported'].tail(5).mean() <= df_national.loc[df_national.last_valid_index()]['Total_infected_locations_reported'] else -1

cards['rivm-current-nursing-homes-infected-locations'] = {
    'value': nursing_homes_reported_infected,
    'title': 'Nursing homes total number of infected locations',
    'color': 'green' if trend <= 0 else 'red',
    'trend': trend
}




df_vacc = pd.read_csv('html/ecdc_vacc.csv')
vacc_latest = df_vacc.iloc[-1]



col = 'percentage_population_vaccinated'
c = 'green' if vacc_latest[col] > 70 else 'blue'
cards['percentage-pop-card'] = {
    'value': f"{fnum(vacc_latest[col], 1)}%",
    'title': 'Percentage population vaccinated with at least one dose',
    'color': c,
}

col = 'percentage_population_fully_vaccinated'
c = 'green' if vacc_latest[col] > 70 else 'blue'
cards['percentage-pop-fully-card'] = {
    'value': f"{fnum(vacc_latest[col], 1)}%",
    'title': 'Percentage population fully vaccinated',
    'color': c,
}

col = 'percentage_population_dose_additional1'
c = 'green' if vacc_latest[col] > 70 else 'blue'
cards['percentage-pop-booster1-card'] = {
    'value': f"{fnum(vacc_latest[col], 1)}%",
    'title': 'Percentage population boosted',
    'color': c,
}


cards['vaccine-total-doses-administered'] = {
    'value': f"{fnum(vacc_latest['total_doses_administered'], 0)}",
    'title': 'Total doses administered',
    'color': 'blue',
}

df_denylist = pd.read_csv('html/qr-denylist.csv', index_col=0)
latest = df_denylist.iloc[-1]

cards['qr-codes-blocked-count'] = {
    'value': f"{fnum(int(latest['num_total']))}",
    'title': "CoronaCheck QR Codes blocked",
    'color': 'blue',
}


output_path = Path('./html/')

from pprint import pprint
pprint(cards)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return round(float(obj), 2)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

with open(output_path / 'cards.json', 'w') as fh:
    json.dump(cards, fh, cls=NpEncoder)
