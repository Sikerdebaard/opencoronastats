import yaml
from datetime import datetime
from pytz import timezone
from pathlib import Path
import json
import time
import os

output_path = Path('./screenshots')


tz = timezone('Europe/Amsterdam')
last_update = datetime.now().astimezone(tz)
last_update_str = last_update.strftime("%Y%m%d-%H%M")

image = 'sikerdebaard/browsercap:latest'
#image = 'joyzoursky/python-chromedriver:3.8-selenium'

print(last_update_str)

with open('data/charts.yml', 'r') as fh:
    pdata = yaml.safe_load(fh)

cmds = []

pages = {}
for page, data in pdata['pages'].items():
    url = "https://covid-analytics.nl/" + data['file']
    charts = {}
    for chart in data['charts']:
        chart_url = url + '#chart-' + chart['name']
        output = f"{last_update_str}-{data['file'][0: data['file'].rindex('.')]}-{chart['name']}.png"
        charts[chart_url] = output
    pages[data['file'] + '.json'] = charts


for page, data in pages.items():
    workdir = Path('./screenshots')
    pagefile = workdir / page
    with open(workdir / page, 'w') as fh:
        json.dump(data, fh)
    dockercmd = f"docker run --rm -w /usr/workspace -v {workdir.absolute()}:/usr/workspace {image} bash -c \"python screencap.py '{page}'\""
    print(dockercmd)
    cmds.append(dockercmd)

from multiprocessing import Pool

def runcmd(cmd):
    os.system(cmd)
    

with Pool(processes=8) as pool:
    result = pool.map(runcmd, cmds)

