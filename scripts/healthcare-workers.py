import requests
from pathlib import Path
import pandas as pd

cachedir = Path('cache')

cachedir.mkdir(parents=True, exist_ok=True)

def download_file(url, output_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

def download_reports_list():
    df_reports = pd.read_csv('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/reports/reports_metadata.csv')
    
    for idx, row in df_reports.iterrows():
        outfile = cachedir / row['filename']
        if not outfile.exists():
            download_file(f'https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/reports/{row["filename"]}', outfile)

download_reports_list()


import pdfplumber
import re
import json


matchers = {
    'infected': r"(\d+)\s+zorgmedewerkers\s+in",
    'hospitalised': r"(\d+)\s+gemeld\s+als\s+opgenomen",
    'deceased': r"(\d+)\s+zorgmedewerkers\s+is\s+gerapporteerd"

}



def convert_to_text(file, ignore_cache=False):
    pages = []
    cachefile = cachedir / (file.resolve().stem + '.json')

    if not ignore_cache and cachefile.exists():
        with open(cachefile, 'r') as fh:
            return json.load(fh)

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text())

    with open(cachefile, 'w') as fh:
        json.dump(pages, fh)

    return pages

def healthcare_workers(pages):
    pages = convert_to_text(file)
    output = {}
    for page in pages:
        for var, pattern in matchers.items():
            matches = re.search(
                pattern,
                page,
                re.MULTILINE
            )

            try:
                num = int(matches.group(1))
                output[var] = num
            except AttributeError:
                pass

    return output


healthcare_worker_nums = {}
files = list(cachedir.glob('*.pdf'))
counter = 1
for file in files:
    print(f'Working on {counter}/{len(files)} {file.name}')
    counter += 1
    if 'epidemiological_report' in file.name:
        pages = convert_to_text(file)
        date = file.name.split('_')[-1].split('.')[0]
        nums = healthcare_workers(pages)
        if nums:
            print(date, nums)
            healthcare_worker_nums[date] = nums

healthcare_workers_manual_corrections = {  # manual corrections due to errors in reports
    '20200929': {'deceased': 13}  # in report 20201006 the number of deceased was said to be wrong for the previous report (20200929), this was corrected to 13
}

for r, v in healthcare_workers_manual_corrections.items():
    healthcare_worker_nums[r].update(v)
    print(healthcare_worker_nums[r])


df_healthcare_workers = pd.DataFrame.from_dict(healthcare_worker_nums, orient='index').sort_index()
df_healthcare_workers.index = pd.to_datetime(df_healthcare_workers.index)
df_healthcare_workers = df_healthcare_workers.resample('W-MON', label='left', closed='left').last()
df_healthcare_workers.index = df_healthcare_workers.index.strftime('%Y-%U')

# create weekly and cumulative, remove first row and convert to int
df_healthcare_workers = df_healthcare_workers.join(df_healthcare_workers.diff(), lsuffix='_cum')[1:].astype(int)

df_gem = pd.read_json('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.json')

df_gem['Date_of_publication'] = pd.to_datetime(df_gem['Date_of_publication'])
df_gem = df_gem.set_index('Date_of_publication')

df_casecounts = df_gem.resample('W-MON', label='left', closed='left').sum()
df_casecounts.index = df_casecounts.index + pd.DateOffset(days=7) # + 7 days offset to shift one week up to get the correct week
df_casecounts.index = df_casecounts.index.strftime('%Y-%U')

df_healthcare_workers['total_population_infected'] = df_casecounts['Total_reported']
df_healthcare_workers['infected_perc_of_total'] = df_healthcare_workers['infected'] / df_casecounts['Total_reported']
df_healthcare_workers['infected_perc_of_total'] = df_healthcare_workers['infected_perc_of_total'].round(3)

df_healthcare_workers.to_csv('html/healthcare-workers.csv', index_label='year-week')
