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

cards['rivm-total-hospitalized'] = {
    'value': fnum(df_rivm['hospitalized_cumulative'].loc[df_rivm['hospitalized_cumulative'].last_valid_index()].astype(int)),
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




df_vaccinated_daily = pd.read_csv('html/daily-vaccine-rollout.csv', index_col=0)
df_vaccinated_daily.index = pd.to_datetime(df_vaccinated_daily.index)

df_model = pd.read_csv('html/vaccinated-estimate-latest.csv', index_col=0)

df_vaccinated_weekly = pd.read_csv('html/weekly-vaccine-rollout.csv', index_col=0)


latest_daily = df_vaccinated_daily.iloc[-1]
latest_weekly = df_vaccinated_weekly.iloc[-1]
latest_model = df_model.iloc[-1]



#from datetime import date
#weekday = date.today().weekday() + 1  # python weekday starts at 0 = Monday
#projection = df_vaccinated_weekly.iloc[-1]['daily_vaccinations_raw'] / weekday * 7  # extremely simplified projection, this needs to be improved once more data is available
#trend = 1 if projection >= df_vaccinated_weekly.iloc[-2]['daily_vaccinations_raw'] else -1

c = 'blue' if int(latest_model['percentage_pop_fully_vaccinated']) != int(latest_model['percentage_pop_vaccinated']) else 'green'
cards['percentage-pop-card'] = {
    'value': f"{int(latest_model['percentage_pop_vaccinated'])}%",
    'title': 'Percentage population vaccinated (partial + fully)',
    'color': 'blue',
}
cards['percentage-pop-fully-card'] = {
    'value': f"{int(latest_model['percentage_pop_fully_vaccinated'])}%",
    'title': 'Percentage population fully vaccinated',
    'color': 'green',
}

cards['vaccine-total-doses-administered'] = {
    'value': f"{fnum(int(latest_daily['total_vaccinations']))}",
    'title': 'Total doses administered',
    'color': 'blue',
}
cards['vaccine-one-in-hundred-people-doses-administered'] = {
    'value': f"{round(float(latest_daily['total_vaccinations_per_hundred']), 2)}/100",
    'title': 'People vaccinated per hundred',
    'color': 'blue',
}

trend = 1 if df_vaccinated_daily.iloc[-1]['sma7_daily_vaccinations'] > df_vaccinated_daily.iloc[-2]['sma7_daily_vaccinations'] else -1
cards['avg-doses-per-week'] = {
    'value': f"{fnum(int(latest_daily['sma7_daily_vaccinations']))}",
    'title': "Rolling average doses per day",
    'color': 'green' if trend == 1 else 'red',
    'trend': trend
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
