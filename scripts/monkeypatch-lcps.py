import pandas as pd
import sys

infile = 'html/data.csv'

df = pd.read_csv(infile)

if not pd.isnull(df['lcps_beds'].iloc[-1]):
    print('CoronaWatchNL up-to-date, not monkey patching')
    sys.exit(0)

import dateparser
from datetime import datetime
import re
from requests import Session
from retry_requests import retry
from bs4 import BeautifulSoup


LCPS_API_URL = 'https://lcps.nu/nieuws/'  # noqa


def htmltoobj(content):
    soup = BeautifulSoup(content, 'html.parser')
    updates = []

    for post in soup.select('div.post'):
        title = post.select_one('h3').text
        date = post.select_one('span.meta span').text
        content = post.select_one('div.excerpt').text

        updates.append({
            "title": title.strip(),
            "date": date.strip(),
            "content": content.strip()
        })

    return {'updates': updates}


def get(url):
    session = retry(Session(), retries=10, backoff_factor=0.2)

    headers = {'User-Agent': 'curl/7.51.0'}  # curl is fine, requests is not :/
    ret = session.get(url, headers=headers)

    while ret.status_code != 200:  # keep trying until we succeed
        ret = session.get(url)

    return ret


def titlenormalizer(title):
    return ' '.join(title.split(' ')[0:2]).replace('.', '').lower().strip()


def titleclassifier(title):
    split = title.split(' ')

    if len(split) != 2:
        return False

    try:

        if split[1].startswith('covid') or split[1].startswith('corona'):
            return True

    except ValueError:
        pass

    return False

def kliniekextractor(title):
    if 'kliniek' in title.lower():
        return int(re.sub('[^0-9]', '', title.split(',')[1].strip().split(' ')[0]))
    return None


news = htmltoobj(get(LCPS_API_URL).content)

year = datetime.now().year

data = []

for item in news['updates']:
    title = titlenormalizer(item['title'])

    if titleclassifier(title):
        patients = int(title.split(' ')[0])

        date = str(dateparser.parse(item['date'], languages=["nl"]).date())

        kliniek = kliniekextractor(item['title'])

        matches = re.search(
            r"(\d+)\s+in\s+Duitsland",
            item['content'],
            re.MULTILINE
        )
        patients_in_de = 0
        try:
            patients_in_de = int(matches.group(1))
        except AttributeError:
            pass

        data.append({'Date': date, 'Aantal': patients,
                     'AantalDuitsland': patients_in_de,
                     'AantalKliniek': kliniek})

df_lcps = pd.DataFrame(data).set_index('Date')
df_lcps.index = pd.to_datetime(df_lcps.index)
df_lcps = df_lcps.sort_index()

df = df.set_index('date')
df.index = pd.to_datetime(df.index)
df_lcps.index = pd.to_datetime(df_lcps.index)
df['lcps_beds'] = df['lcps_beds'].combine_first(df_lcps['Aantal'])

df.to_csv(infile)


df = pd.read_csv('html/hospitalized.csv')

df = df.set_index('date')
df.index = pd.to_datetime(df.index)

df['lcps_beds'] = df['lcps_beds'].combine_first(df_lcps['AantalKliniek'])

df.to_csv('html/hospitalized.csv')
