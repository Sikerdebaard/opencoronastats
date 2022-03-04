import pandas as pd
import sys


# ## RIVM Data: cumulative case counts by municipalities
# [This dataset can be found here.](https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/1c0fcd57-1102-4620-9cfa-441e93ea5604?tab=relations) It comprises a dataset with cumulative case-counts on a municipality level. We are going to load it into a pandas dataframe and then convert it from a municipality level to a national level after which we resample it from day-to-day numbers to weekly numbers. 
# 
# We assume the week starts on Mondays, as this is the standard in the Netherlands.

# In[3]:


df = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.json')

df['Date_of_report'] = pd.to_datetime(df['Date_of_report']) # convert column from int to datetime
df = df.set_index('Date_of_report') # set column as index

df_daily_cum = df.resample('D').sum() # resample to daily
    
df_daily_cum.rename(columns={'Total_reported': 'infected', 'Deceased': 'deceased'}, inplace=True)
df_daily_cum.index.rename('date', inplace=True)

#df_daily_cum.to_csv('daily_cumulative_from_municipality.csv')

df_weekly_cum = df_daily_cum.resample('W-MON', label='left', closed='left').max()  # label=left prevents off-by-one error in weeknum
#df_weekly_cum.index = df_weekly_cum.index.week

#df_weekly_cum.index = df_weekly_cum.index.week
df_weekly_cum.index = df_weekly_cum.index.strftime('%G-%V')


df_weekly_cum.index.rename('week', inplace=True)
#df_weekly_cum.to_csv('weekly_cumulative_from_municipality.csv')


total_deaths = df_weekly_cum['deceased'].iloc[-1]
total_infected = df_weekly_cum['infected'].iloc[-1]
print(f'Total deaths: {total_deaths}')
print(f'Total infected: {total_infected}')


# ## RIVM Data: intra-day case counts by municipality
# 
# [This dataset can be found here.](https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/5f6bc429-1596-490e-8618-1ed8fd768427) It comprises the same data as the dataset above but instead of being cumulative data this dataset is intra-day.
# 
# We will again assume the week start on a Monday as is usual in the Netherlands.

# In[4]:


df = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.json')

df['Date_of_publication'] = pd.to_datetime(df['Date_of_publication'])
df = df.set_index('Date_of_publication')

df_daily = df.resample('D').sum()
    
df_daily.rename(columns={'Total_reported': 'infected', 'Deceased': 'deceased'}, inplace=True)
df_daily.index.rename('date', inplace=True)

#df_daily.to_csv('daily_from_municipality.csv')

df_weekly = df_daily.resample('W-MON', label='left', closed='left').sum()  # label=left prevents off-by-one error in weeknum
#df_weekly.index = df_weekly.index.week

#df_weekly.index = df_weekly.index.week
df_weekly.index = df_weekly.index.strftime('%G-%V')

df_weekly.index.rename('week', inplace=True)
#df_weekly.to_csv('weekly_from_municipality.csv')

total_deaths = df_weekly['deceased'].sum()
total_infected = df_weekly['infected'].sum()
print(f'Total deaths: {total_deaths}')
print(f'Total infected: {total_infected}')


# ## RIVM Data: intra-day case counts by individual case reports
# 
# [This dataset can be found here.](https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724) So this dataset is quite interesting. It comprises of individual case counts. So information about the age group, sex, province, hospital admission, deceased, week_of_death and municipal health service are listed in here for everyone that was registered COVID-19 positive by the RIVM. This dataset also contains datetime info on when the first symptoms appeared for (at the time of writing) about 80% of the participants.
# 
# Based on the column 'Deceased' and 'Week_of_death' we can calculate the number of deceased. The total number of infected is simply the size (rows) in the dataframe. We do however need to do some data manipulation in order to resample it to a weekly interval.

# In[5]:


df_casus = pd.read_csv('https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv', sep=';')

deceased_extra = 0

df_validate = df_casus[(df_casus['Deceased'] == 'No') & (df_casus['Week_of_death'] >= 0)]
if df_validate.shape[0] > 0:
    #print(f'Deceased No but Week of death > 0 [{df_validate.shape[0]}]', df_validate)
    deceased_extra += df_validate.shape[0]
    
df_validate = df_casus[(df_casus['Deceased'] == 'Yes') & (df_casus['Week_of_death'].isnull())]
if df_validate.shape[0] > 0:
    #print(f'Deceased Yes but no Week of death [{df_validate.shape[0]}]', df_validate)
    deceased_extra += df_validate.shape[0]
    
df_deceased = df_casus[(df_casus['Deceased'] == 'Yes') & ~(df_casus['Week_of_death'].isnull())]
#print(f'Deceased Yes with week of death [{df_deceased.shape[0]}]', df_deceased)

df_intermediate = df_deceased[['Date_file', 'Date_statistics', 'Week_of_death']].copy()
df_intermediate


#df_intermediate['Week_of_death'] = df_intermediate['Week_of_death'] - 1 + 0.6 # actually - 0.4 prevent off-by-one error in weeks and set day on sunday
df_intermediate['Week_of_death'] = pd.to_datetime(df_intermediate['Week_of_death'].astype(str), format='%G%V.%w')
df_intermediate['Week_of_death'] = df_intermediate['Week_of_death'].dt.strftime('%G-%V')

# # First deaths
df_deceased = pd.DataFrame(df_intermediate.groupby(['Week_of_death']).count()['Date_statistics'].rename('deceased'))
df_deceased.index.rename('weeknum', inplace=True)  # rename index to something more pleasing

df_deceased

total_deceased = df_deceased['deceased'].sum()
print(f'Unaccounted deaths in weekly deaths due to unknown date or conflicting data: {deceased_extra}')
print(f'Total deaths including unaccounted deaths: {total_deceased + deceased_extra}')


# Now infected
df_infected = df_casus.copy()
df_infected['Date_statistics'] = pd.to_datetime(df_infected['Date_statistics'])
df_infected = pd.DataFrame(df_infected.resample('W-MON', label='left', on='Date_statistics', closed='left').count()['Date_statistics'])
#df_infected.index = df_infected.index.week
#df_infected.index = df_infected.index.week
df_infected.index = df_infected.index.strftime('%G-%V')
df_infected.rename(columns={'Date_statistics': 'infected'}, inplace=True)
df_infected.index.rename('weeknum', inplace=True)

# Infected can be done daily
#df_daily_infected = df_casus.copy()
#df_daily_infected['Date_statistics'] = pd.to_datetime(df_daily_infected['Date_statistics'])
#df_daily_infected = pd.DataFrame(df_daily_infected.resample('D', label='left', on='Date_statistics').count()['Date_statistics'])
#df_daily_infected.index = df_daily_infected.index.week
#df_daily_infected.rename(columns={'Date_statistics': 'infected'}, inplace=True)
#df_daily_infected.index.rename('weeknum', inplace=True)

infected = df_infected['infected'].sum()
print(f'Total infected: {infected}')

# Get some numbers on when Date_statistics was set
#DOO = Date of disease onset
#DPL = Date of first Positive Labresult
#DON = Date of Notification
rows = df_casus.shape[0]
vals = dict(df_casus['Date_statistics_type'].value_counts())

print('Distribution of Date_statistics_type')
for k, v in vals.items():
    print(f'{k}: {v/rows:.3f}')

# Hospitalized is not really possible, there's no date on when the admission took place in the dataset


#df_deceased.to_csv('weekly_from_casereports.csv')



# ## Merging the different datasets
# Lets merge all the different datasets together and get it ready for plotting.
# 
# There will be two types of plots: cumulative and intra-day.
# For this we will convert datasets between these two formats. E.g. when generating intra-day plots we will plot all intra-day datasets but also attempt to convert the cumulative datasets to intra-day. We will do the same when plotting the cumulative charts, just the other way around.

# In[9]:






### GGD


import pandas as pd


df_ggd = pd.read_csv('https://data.rivm.nl/covid-19/COVID-19_uitgevoerde_testen.csv', sep=';').set_index('Date_of_statistics')
df_ggd.index = pd.to_datetime(df_ggd.index)

df_ggd = df_ggd.groupby(df_ggd.index).sum().sort_index().drop(columns=['Version'])['Tested_positive'].rename('GGD positive tests')

df_ggd.index = df_ggd.index.map(lambda x: x.strftime('%G-%V'))
df_ggd = df_ggd.groupby(df_ggd.index).sum()

df_ggd_cum = df_ggd.cumsum().rename(f'{df_ggd.name} cumulative')

### /> GGD





### NICE registered deaths
import requests


req = requests.get('https://raw.githubusercontent.com/Sikerdebaard/dutchcovid19data/master/data/died-and-survivors-cumulative.json')
req.raise_for_status()

df_icu = pd.DataFrame(req.json()['data'][0])
df_icu['date'] = pd.to_datetime(df_icu['date'])
df_icu.set_index('date', inplace=True)
df_icu.sort_index(inplace=True)

req = requests.get('https://raw.githubusercontent.com/Sikerdebaard/dutchcovid19data/master/data/hospitalized/died-and-survivors-cumulative.json')
req.raise_for_status()

df_hosp = pd.DataFrame(req.json()['data'][0])
df_hosp['date'] = pd.to_datetime(df_hosp['date'])
df_hosp.set_index('date', inplace=True)
df_hosp.sort_index(inplace=True)

df_nice_merged = pd.DataFrame(index=(df_hosp.index.union(df_icu.index)))

df_nice_merged = df_nice_merged.join(df_icu['value'].rename('deceased_icu'))
df_nice_merged = df_nice_merged.join(df_hosp['value'].rename('deceased_hospital'))

df_nice_merged['deceased_icu_hospital'] = df_nice_merged.sum(axis=1)

df_nice_merged_weekly = df_nice_merged.resample('W-SUN').last()
df_nice_merged_weekly.index = df_nice_merged_weekly.index.map(lambda x: x.strftime('%G-%V'))
df_nice_merged_weekly.index.rename('YearWeek', inplace=True)

df_nice_merged_weekly_diff = df_nice_merged_weekly.diff().fillna(0).astype(int)

### /> NICE




df_merged = df_infected.copy()
df_merged = df_merged.join(df_deceased)

# first cumulative RIVM data

df_merged_cum = df_merged.cumsum()  # cumulative df
df_merged_cum = df_merged_cum.add_prefix('casereports_cumulative_')
df_merged_cum = df_merged_cum.join(df_weekly_cum.add_prefix('municipality_cumulative_'))
#df_merged_cum = df_merged_cum.join(df_weekly.cumsum().add_prefix('municipality_')) # convert intra to cum
df_merged_cum = df_merged_cum.add_prefix('rivm_')


#df_merged_cum.to_csv('merged_cumulative.csv')

# first intra-day RIVM data                                   
                                   
df_merged = df_merged.add_prefix('casereports_')
#df_merged = df_merged.join(df_weekly_cum.diff().add_prefix('municipality_cumulative_')) # convert cum to intra
df_merged = df_merged.join(df_weekly.add_prefix('municipality_'))
df_merged = df_merged.add_prefix('rivm_')

# then intra CoronaWatchNL data


#df_merged.to_csv('merged.csv')


# ## Lets get plotting!
# 
# 
# Lets first import matplotlib and set the DPI so that the charts are rendered in a nice resolution.

# In[10]:

df_infected = df_merged.loc[:,df_merged.columns.str.contains('_infected')]
df_infected.columns = [' '.join(c.split('_')[:-1]) for c in df_infected.columns]
df_infected = df_infected.join(df_ggd)
df_infected.to_csv('./html/infected.csv')
df_infected_cum = df_merged_cum.loc[:,df_merged_cum.columns.str.contains('_infected')]
df_infected_cum.columns = [' '.join(c.split('_')[:-1]) for c in df_infected_cum.columns]
df_infected_cum = df_infected_cum.join(df_ggd_cum)
df_infected_cum.to_csv('./html/infected_cumulative.csv')

df_deceased = df_merged.loc[:,df_merged.columns.str.contains('_deceased')]
df_deceased.columns = [' '.join(c.split('_')[:-1]) for c in df_deceased.columns]
df_deceased = df_deceased.join(df_nice_merged_weekly_diff['deceased_icu_hospital'].rename('Stichting NICE registration (hospital + ICU)'))
df_deceased.to_csv('./html/deceased.csv')
df_deceased_cum = df_merged_cum.loc[:,df_merged_cum.columns.str.contains('_deceased')]
df_deceased_cum.columns = [' '.join(c.split('_')[:-1]) for c in df_deceased_cum.columns]
df_deceased_cum = df_deceased_cum.join(df_nice_merged_weekly['deceased_icu_hospital'].rename('Stichting NICE registration cumulative (hospital + ICU)'))
df_deceased_cum.to_csv('./html/deceased_cumulative.csv')



## estimated infected and reproduction index

df_repro = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json')
df_repro['Date'] = pd.to_datetime(df_repro['Date'])

df_repro = df_repro.rename(columns={'Date': 'datum', 'Rt_low': 'r_min', 'Rt_up': 'r_max', 'Rt_avg': 'r'})[['datum', 'r_min', 'r', 'r_max']]

df_repro.set_index(['datum'], inplace=True)

df_cont = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_prevalentie.json')



df_cont['Date'] = pd.to_datetime(df_cont['Date'])

df_cont = df_cont.rename(columns={'Date': 'date', 'prev_low': 'contagious_min', 'prev_avg': 'contagious', 'prev_up': 'contagious_max'})[['date', 'contagious_min', 'contagious', 'contagious_max']]
df_cont.set_index(['date'], inplace=True)

df_merged = pd.DataFrame(index=df_cont.index.union(df_repro.index))

df_merged = df_merged.join(df_cont)
df_merged = df_merged.join(df_repro)

df_merged.index.rename('Datum', inplace=True)

df_merged.to_csv('html/infection.csv')
