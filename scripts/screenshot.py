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

print(last_update_str)

with open('data/charts.yml', 'r') as fh:
    pdata = yaml.safe_load(fh)

cmds = []

for page, data in pdata['pages'].items():
    url = "https://covid-analytics.nl/" + data['file']
    for chart in data['charts']:
        chart_url = url + '#chart-' + chart['name']
        output = f"{last_update_str}-{data['file'][0: data['file'].rindex('.')]}-{chart['name']}.png"
        workdir = Path('./screenshots')
        dockercmd = f"docker run -it -w /usr/workspace -v {workdir.absolute()}:/usr/workspace joyzoursky/python-chromedriver:3.8-selenium bash -c \"python screencap.py '{chart_url}' {output}\""
        print(dockercmd)
        cmds.append(dockercmd)


from multiprocessing import Pool

def runcmd(cmd):
    os.system(cmd)
    

with Pool(processes=2) as pool:
    result = pool.map(runcmd, cmds)

