import pandas as pd

df_denylist = pd.read_csv('https://raw.githubusercontent.com/Sikerdebaard/coronacheck-denylist/main/data/latest-denylist.csv', index_col=0)
df_denylist.to_csv('html/qr-denylist.csv')
