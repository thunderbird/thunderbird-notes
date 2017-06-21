import jinja2
import markdown
import os
import yaml

from gettext import NullTranslations

notesfile = "52.2.1.yaml"

with open(notesfile, 'r') as f:
    doc = yaml.load(f)

def get_bug_search_url():
    return doc["release"]["bug_search_url"]

def safe_markdown(text):
    if not text:
        text = ''
    return jinja2.Markup(markdown.markdown(text))

def l10n_format_date(text):
    return text

def url(*args, **kwargs):
    return ''

class Translation(object):
    def gettext(self, text):
        return text
    ugettext = gettext
    ngettext = gettext

translator = Translation()

doc["release"]["get_bug_search_url"] = get_bug_search_url

jinja_env = jinja2.Environment(
    extensions = ["jinja2.ext.i18n"],
    loader = jinja2.FileSystemLoader(os.path.abspath('./template')),
)
jinja_env.globals.update(url=url)
jinja_env.filters['markdown'] = safe_markdown
jinja_env.filters['f'] = jinja_env.filters['format']
jinja_env.filters['l10n_format_date'] = l10n_format_date
jinja_env.install_gettext_translations(translator)
template = jinja_env.get_template('release-notes.html')
print(template.render(**doc))
