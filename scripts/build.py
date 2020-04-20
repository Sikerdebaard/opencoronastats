import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape, Markup
import markdown
from markdown.extensions.toc import TocExtension


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

md = markdown.Markdown(extensions=['meta', 'toc'])

env.filters['markdown'] = lambda text: Markup(md.convert(text))
env.filters['stylize'] = lambda text: Markup(md.convert(text))

for page, data in pdata['pages'].items():
    template = env.get_template('page.html.jinja')
    page = template.render(template='stats.html.jinja', version=123, chart_config=pdata['chart_config'], page=page, data=data, charts=group_by_two(data['charts']), cards=group_by_two(data['cards']))

    with open(f'html/{data["file"]}', 'w') as fh:
        fh.write(page)

markdown_pages = ['explanation.md']

for markdown_page in markdown_pages:
    with open(f'templates/{markdown_page}', 'r') as fh:
        mdcontent = fh.read()

    template = env.get_template('page.html.jinja')
    page = template.render(template='markdown.html.jinja', version=123, content=mdcontent)

    with open(f'html/{markdown_page.rsplit(".", 1)[0]}.html', 'w') as fh:
        fh.write(page)