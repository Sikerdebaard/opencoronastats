import pandas as pd

df = pd.read_html('https://www.rivm.nl/covid-19-vaccinatie/cijfers-vaccinatieprogramma', thousands='.', decimal=',')[0]
df.columns = ['target_group', 'subgroup', 'number_of_people']

# Print total number of people that received at least one dose
df_demographics = df[~df['target_group'].str.contains('Totaal').fillna(False)]
df_demographics = df_demographics[~df_demographics['subgroup'].isna()][['subgroup', 'number_of_people']]
df_demographics['number_of_people'] = df_demographics['number_of_people'].astype(int)

translations = {
    'Ziekenhuismedewerkers acute zorg': 'Acute Care Workers',
    'Verpleeghuismedewerkers': 'Nursing Home Care Workers',
}
df_demographics['subgroup'] = df_demographics['subgroup'].replace(translations)

df_demographics.to_csv('html/vaccinated-demographics.csv', index=False)
