import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


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
    data = yaml.safe_load(fh)

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['jinja'])
)

for page, data in data['pages'].items():
    template = env.get_template('page.html.jinja')
    print(template.render(version=123, page=page, data=data, charts=group_by_two(data['charts']), cards=group_by_two(data['cards'])))