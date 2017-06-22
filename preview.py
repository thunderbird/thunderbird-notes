# -*- coding: utf-8 -*-

import argparse
import jinja2
import markdown
import os
import sys
import yaml

parser = argparse.ArgumentParser(
    description="""
    Enter the file name of the .yml file you want to preview.
    Example: `python preview.py 52.2.1.yml`
    """, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("notesfile", help="name of the release notes .yml file to preview")

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

with open(args.notesfile, "r") as f:
    doc = yaml.load(f)

with open("settings.yml", "r") as f:
    s = yaml.load(f)
    doc["feedback"] = s["feedback"]
    doc["bugzilla"] = s["bugzilla"]

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

