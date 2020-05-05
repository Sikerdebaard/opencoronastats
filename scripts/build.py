import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape, Markup
import markdown
from datetime import datetime
from pytz import timezone
from pathlib import Path
import json

output_path = Path('./html/')

tz = timezone('Europe/Amsterdam')
last_update = datetime.now().astimezone(tz)
last_update_str = last_update.strftime("%d-%m-%Y %H:%M")

print(last_update_str)

with (output_path / 'timestamp.json').open('w') as fh:
    json.dump(last_update.isoformat(), fh)




def group_by_two(arr):
    if arr is None:
        return []
    output = []
    for i in range(0, len(arr), 2):
        if i+1 < len(arr):
            output.append([arr[i], arr[i+1]])
        else:
            output.append([arr[i]])

    return output



with open('data/charts.yml', 'r') as fh:
    pdata = yaml.safe_load(fh)

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['jinja'])
)

md = markdown.Markdown(extensions=['meta', 'toc', 'sane_lists'])

env.filters['markdown'] = lambda text: Markup(md.convert(text))
env.filters['stylize'] = lambda text: Markup(md.convert(text))

for page, data in pdata['pages'].items():
    if 'cards' in data:
        if data['cards'] is None:
            card_keys = []
        else:
            card_keys = [x['id'] for x in data['cards']]
    else:
        card_keys = []

    template = env.get_template('page.html.jinja')
    page = template.render(last_update=last_update_str, template='stats.html.jinja', version=123, chart_config=pdata['chart_config'], page=page, data=data, charts=group_by_two(data['charts']), cards=group_by_two(data['cards']), card_keys=card_keys)

    with open(f'html/{data["file"]}', 'w') as fh:
        fh.write(page)

markdown_pages = ['explanation.md', 'changelog.md', 'about.md']

for markdown_page in markdown_pages:
    with open(f'templates/{markdown_page}', 'r') as fh:
        mdcontent = fh.read()

    page_name = markdown_page.rsplit(".", 1)[0]
    template = env.get_template('page.html.jinja')
    page = template.render(last_update=last_update_str, template='markdown.html.jinja', version=123, content=mdcontent, page=page_name)

    with open(f'html/{page_name}.html', 'w') as fh:
        fh.write(page)