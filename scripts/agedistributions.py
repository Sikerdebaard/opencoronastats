import pandas as pd

df_casus = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json')
df_tf = df_casus.copy()



# First infected age distribution

df_tf['Date_statistics'] = pd.to_datetime(df_tf['Date_statistics'])

df_age = df_tf.groupby(['Agegroup'])[['Date_statistics']].resample('W-MON', label='left', on='Date_statistics').count().rename(columns={'Date_statistics': 'count'})


df_age = df_age.reset_index()
df_age = df_age.pivot(index='Date_statistics', columns='Agegroup', values='count')

df_age = df_age.div(df_age.sum(axis=1), axis=0) # normalize to percentage
df_age[df_age.select_dtypes(include=['number']).columns] *= 100

df_age = df_age[4:]  # cut off first few cases, too little cases to visualize
df_age = df_age.round(1)

df_age.to_csv('html/casus-by-age.csv')

df_age


# Second deaths age distribution

df_tf = df_casus[(df_casus['Deceased'] == 'Yes') & ~(df_casus['Week_of_death'].isnull())][['Date_file', 'Date_statistics', 'Week_of_death', 'Agegroup']].copy()
df_tf['Week_of_death'] = df_tf['Week_of_death'] - 1 + 0.6
df_tf['Week_of_death'] = pd.to_datetime(df_tf['Week_of_death'].astype(str), format='%Y%U.%w')

df_deceased = df_tf.groupby(['Agegroup'])[['Week_of_death']].resample('W-MON', label='left', on='Week_of_death').count().rename(columns={'Week_of_death': 'count'})


df_deceased = df_deceased.reset_index()
df_deceased = df_deceased.pivot(index='Week_of_death', columns='Agegroup', values='count')

df_deceased = df_deceased.div(df_deceased.sum(axis=1), axis=0)

df_deceased[df_deceased.select_dtypes(include=['number']).columns] *= 100
df_deceased = df_deceased.round(1)

df_deceased.to_csv('html/deceased-by-age.csv')
