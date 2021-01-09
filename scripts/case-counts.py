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
    
df_daily_cum.rename(columns={'Total_reported': 'infected', 'Hospital_admission':  'hospitalized', 'Deceased': 'deceased'}, inplace=True)
df_daily_cum.index.rename('date', inplace=True)

#df_daily_cum.to_csv('daily_cumulative_from_municipality.csv')

df_weekly_cum = df_daily_cum.resample('W-MON', label='left', closed='left').max()  # label=left prevents off-by-one error in weeknum
#df_weekly_cum.index = df_weekly_cum.index.week

#df_weekly_cum.index = df_weekly_cum.index.week
df_weekly_cum.index = df_weekly_cum.index.strftime('%Y-%U')


df_weekly_cum.index.rename('week', inplace=True)
#df_weekly_cum.to_csv('weekly_cumulative_from_municipality.csv')


total_deaths = df_weekly_cum['deceased'].iloc[-1]
total_hospitalized = df_weekly_cum['hospitalized'].iloc[-1]
total_infected = df_weekly_cum['infected'].iloc[-1]
print(f'Total deaths: {total_deaths}')
print(f'Total hospitalized: {total_hospitalized}')
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
    
df_daily.rename(columns={'Total_reported': 'infected', 'Hospital_admission':  'hospitalized', 'Deceased': 'deceased'}, inplace=True)
df_daily.index.rename('date', inplace=True)

#df_daily.to_csv('daily_from_municipality.csv')

df_weekly = df_daily.resample('W-MON', label='left', closed='left').sum()  # label=left prevents off-by-one error in weeknum
#df_weekly.index = df_weekly.index.week

#df_weekly.index = df_weekly.index.week
df_weekly.index = df_weekly.index.strftime('%Y-%U')

df_weekly.index.rename('week', inplace=True)
#df_weekly.to_csv('weekly_from_municipality.csv')

total_deaths = df_weekly['deceased'].sum()
total_hospitalized = df_weekly['hospitalized'].sum()
total_infected = df_weekly['infected'].sum()
print(f'Total deaths: {total_deaths}')
print(f'Total hospitalized: {total_hospitalized}')
print(f'Total infected: {total_infected}')


# ## RIVM Data: intra-day case counts by individual case reports
# 
# [This dataset can be found here.](https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724) So this dataset is quite interesting. It comprises of individual case counts. So information about the age group, sex, province, hospital admission, deceased, week_of_death and municipal health service are listed in here for everyone that was registered COVID-19 positive by the RIVM. This dataset also contains datetime info on when the first symptoms appeared for (at the time of writing) about 80% of the participants.
# 
# Based on the column 'Deceased' and 'Week_of_death' we can calculate the number of deceased. The total number of infected is simply the size (rows) in the dataframe. We do however need to do some data manipulation in order to resample it to a weekly interval.

# In[5]:


df_casus = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json')

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


df_intermediate['Week_of_death'] = df_intermediate['Week_of_death'] - 1 + 0.6 # actually - 0.4 prevent off-by-one error in weeks and set day on sunday
df_intermediate['Week_of_death'] = pd.to_datetime(df_intermediate['Week_of_death'].astype(str), format='%Y%W.%w')
df_intermediate['Week_of_death'] = df_intermediate['Week_of_death'].dt.strftime('%Y-%U')

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
df_infected.index = df_infected.index.strftime('%Y-%U')
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


# ## CoronaWatchNL Data: OSIRISGEO
# [CoronaWatchNL](https://github.com/J535D165/CoronaWatchNL) writes the following about this dataset: "These datasets describe the new and cumulative number of confirmed, hospitalized and deceased COVID-19 cases. Every day, the data is retrieved from the central database OSIRIS at 10:00 AM by RIVM. The datasets are categorized by their geographical level (national, provincial, municipal)."
# 
# Both intra-day and cumulative data is available.

# In[6]:


# OSIRIS
df_osirisgeo = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-geo/data-national/RIVM_NL_national.csv', index_col=0)
df_osirisgeo.index = pd.to_datetime(df_osirisgeo.index)

df_osirisgeo = df_osirisgeo.pivot(columns='Type')

# cumulative data
df_osirisgeo_cum = df_osirisgeo['AantalCumulatief']
df_osirisgeo_cum = df_osirisgeo_cum.resample('W-MON', label='left', closed='left').max().rename(columns={'Overleden': 'deceased', 'Totaal': 'infected', 'Ziekenhuisopname': 'hospital'})
#df_osirisgeo_cum.index = df_osirisgeo_cum.index.week
#df_osirisgeo_cum.index = df_osirisgeo_cum.index.week
df_osirisgeo_cum.index = df_osirisgeo_cum.index.strftime('%Y-%U')

#df_osirisgeo_cum.to_csv('osirisgeo_cum.csv')

# intra-day data
df_osirisgeo = df_osirisgeo['Aantal']

df_osirisgeo = df_osirisgeo.resample('W-MON', label='left', closed='left').sum().rename(columns={'Overleden': 'deceased', 'Totaal': 'infected', 'Ziekenhuisopname': 'hospital'})
#df_osirisgeo.index = df_osirisgeo.index.week
#df_osirisgeo.index = df_osirisgeo.index.week
df_osirisgeo.index = df_osirisgeo.index.strftime('%Y-%U')

#df_osirisgeo.to_csv('osirisgeo.csv')


# ## CoronaWatchNL Data: OSIRIS
# [CoronaWatchNL](https://github.com/J535D165/CoronaWatchNL) writes the following about this dataset: "These datasets describe the new and cumulative number of confirmed, hospitalized and deceased COVID-19 cases per day. The data is retrieved from the central database OSIRIS and counts the number per day (0:00 AM) by RIVM. The dataset concerns numbers on a national level."
# 
# This dataset consists of intra-day case counts.

# In[7]:


# OSIRIS
df_osiris = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data/rivm_NL_covid19_national_by_date/rivm_NL_covid19_national_by_date_latest.csv', index_col=0)
df_osiris.index = pd.to_datetime(df_osiris.index)


df_osiris = df_osiris.pivot(columns='Type')

# intra-day data
df_osiris = df_osiris['Aantal']

df_osiris = df_osiris.resample('W-MON', label='left', closed='left').sum().rename(columns={'Overleden': 'deceased', 'Totaal': 'infected', 'Ziekenhuisopname': 'hospital'})
#df_osiris.index = df_osiris.index.week
#df_osiris.index = df_osiris.index.week
df_osiris.index = df_osiris.index.strftime('%Y-%U')

#df_osiris.to_csv('osiris.csv')


# ## CoronaWatchNL Data: OSIRIS
# [CoronaWatchNL](https://github.com/J535D165/CoronaWatchNL) writes the following about this dataset: "The datasets underlying the National Dashboard are listed in this folder. These datasets concern various topics, such as an overview of the number and age distribution of hospitalized, positively tested, and suspected cases, an estimate of the number of contagious people, the reproduction index, the number of (deceased) infected nursery home residents, and the amount of virus particles measured in the sewage water."
# 
# The National Dashboard in question can be found [here.](https://coronadashboard.government.nl/)
# 
# Currently we are only interested in infected and deceased so thats the dataset that we will download and process.
# 
# Both cumulative data and intra-day data is available.

# In[8]:


# Coronadashboard
df_dashboard = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-cases/RIVM_NL_national_dashboard.csv', index_col=0)
df_dashboard.index = pd.to_datetime(df_dashboard.index)

df_dashboard

df_dashboard = df_dashboard.pivot(columns='Type')

# cumulative data
df_dashboard_cum = df_dashboard['AantalCumulatief']
df_dashboard_cum = df_dashboard_cum.resample('W-MON', label='left', closed='left').max().rename(columns={'Overleden': 'deceased', 'Totaal': 'infected', 'Ziekenhuisopname': 'hospital'})
#df_dashboard_cum.index = df_dashboard_cum.index.week
#df_dashboard_cum.index = df_dashboard_cum.index.week
df_dashboard_cum.index = df_dashboard_cum.index.strftime('%Y-%U')

#df_dashboard_cum.to_csv('dashboard_cum.csv')


# intra-day data
df_dashboard = df_dashboard['Aantal']

df_dashboard = df_dashboard.resample('W-MON', label='left', closed='left').sum().rename(columns={'Totaal': 'infected', 'Ziekenhuisopname': 'hospital'})
#df_dashboard.index = df_dashboard.index.week
#df_dashboard.index = df_dashboard.index.week
df_dashboard.index = df_dashboard.index.strftime('%Y-%U')

#df_dashboard.to_csv('dashboard.csv')


# ## Merging the different datasets
# Lets merge all the different datasets together and get it ready for plotting.
# 
# There will be two types of plots: cumulative and intra-day.
# For this we will convert datasets between these two formats. E.g. when generating intra-day plots we will plot all intra-day datasets but also attempt to convert the cumulative datasets to intra-day. We will do the same when plotting the cumulative charts, just the other way around.

# In[9]:


df_merged = df_infected.copy()
df_merged = df_merged.join(df_deceased)

# first cumulative RIVM data

df_merged_cum = df_merged.cumsum()  # cumulative df
df_merged_cum = df_merged_cum.add_prefix('casereports_cumulative_')
df_merged_cum = df_merged_cum.join(df_weekly_cum.add_prefix('municipality_cumulative_'))
#df_merged_cum = df_merged_cum.join(df_weekly.cumsum().add_prefix('municipality_')) # convert intra to cum
df_merged_cum = df_merged_cum.add_prefix('rivm_')

# then cumulative CoronaWatchNL data
df_merged_cum = df_merged_cum.join(df_osirisgeo_cum.add_prefix('coronawatchnl_osirisgeo_cumulative_'))
#df_merged_cum = df_merged_cum.join(df_osirisgeo.cumsum().add_prefix('coronawatchnl_osirisgeo_')) # convert intra to cum
#df_merged_cum = df_merged_cum.join(df_osiris.cumsum().add_prefix('coronawatchnl_osiris_')) # convert intra to cum
df_merged_cum = df_merged_cum.join(df_dashboard_cum.add_prefix('coronawatchnl_dashboard_cumulative_'))
#df_merged_cum = df_merged_cum.join(df_dashboard.cumsum().add_prefix('coronawatchnl_dashboard_')) # convert intra to cum

#df_merged_cum.to_csv('merged_cumulative.csv')

# first intra-day RIVM data                                   
                                   
df_merged = df_merged.add_prefix('casereports_')
#df_merged = df_merged.join(df_weekly_cum.diff().add_prefix('municipality_cumulative_')) # convert cum to intra
df_merged = df_merged.join(df_weekly.add_prefix('municipality_'))
df_merged = df_merged.add_prefix('rivm_')

# then intra CoronaWatchNL data
#df_merged = df_merged.join(df_osirisgeo_cum.diff().add_prefix('coronawatchnl_osirisgeo_cumulative_')) # convert cum to intra
df_merged = df_merged.join(df_osirisgeo.add_prefix('coronawatchnl_osirisgeo_')) 
df_merged = df_merged.join(df_osiris.add_prefix('coronawatchnl_osiris_')) 
#df_merged = df_merged.join(df_dashboard_cum.diff().add_prefix('coronawatchnl_dashboard_cumulative_')) # convert cum to intra
df_merged = df_merged.join(df_dashboard.add_prefix('coronawatchnl_dashboard_')) 


#df_merged.to_csv('merged.csv')


# ## Lets get plotting!
# 
# 
# Lets first import matplotlib and set the DPI so that the charts are rendered in a nice resolution.

# In[10]:

df_infected = df_merged.loc[:,df_merged.columns.str.contains('_infected')]
df_infected.columns = [' '.join(c.split('_')[:-1]) for c in df_infected.columns]
df_infected.to_csv('./html/infected.csv')
df_infected_cum = df_merged_cum.loc[:,df_merged_cum.columns.str.contains('_infected')]
df_infected_cum.columns = [' '.join(c.split('_')[:-1]) for c in df_infected_cum.columns]
df_infected_cum.to_csv('./html/infected_cumulative.csv')

df_deceased = df_merged.loc[:,df_merged.columns.str.contains('_deceased')]
df_deceased.columns = [' '.join(c.split('_')[:-1]) for c in df_deceased.columns]
df_deceased.to_csv('./html/deceased.csv')
df_deceased_cum = df_merged_cum.loc[:,df_merged_cum.columns.str.contains('_deceased')]
df_deceased_cum.columns = [' '.join(c.split('_')[:-1]) for c in df_deceased_cum.columns]
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
