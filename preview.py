# -*- coding: utf-8 -*-

import jinja2
import markdown
import os
import yaml

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


def f(s, *args, **kwargs):
    return s.format(*args, **kwargs)


class Translation(object):
    def gettext(self, text):
        return text
    ugettext = gettext
    ngettext = gettext

translator = Translation()

# Prepare variables for template rendering.
doc["release"]["get_bug_search_url"] = get_bug_search_url
doc["channel_name"] = "Beta"
doc["channel"] = doc["channel_name"]
doc["version"] = doc["release"]["version"]
doc["known_issues"] = []
doc["new_features"] = []
for note in doc["notes"]:
    if note["tag"] == "unresolved":
        doc["known_issues"].append(note)
    else:
        doc["new_features"].append(note)


jinja_env = jinja2.Environment(
    extensions = ["jinja2.ext.i18n"],
    loader = jinja2.FileSystemLoader(os.path.abspath('./template')),
)
jinja_env.globals.update(url=url)
jinja_env.filters['markdown'] = safe_markdown
jinja_env.filters['f'] = f
jinja_env.filters['l10n_format_date'] = l10n_format_date
jinja_env.install_gettext_translations(translator)
template = jinja_env.get_template('release-notes.html')

with open("preview.html", "wb") as f:
    o = template.render(**doc)
    f.write(o.encode('utf8'))

