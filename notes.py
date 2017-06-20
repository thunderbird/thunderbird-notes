import jinja2
import os
from jinja2 import Template

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.abspath('./template'))
)

template = latex_jinja_env.get_template('release-notes.html')
print(template.render(**project))
