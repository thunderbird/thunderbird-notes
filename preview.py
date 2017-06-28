# -*- coding: utf-8 -*-

import argparse
from loader import ReleaseNotes
import jinja2
import markdown
import os
import sys
import yaml

parser = argparse.ArgumentParser(
    description="""
    Enter the version number you want to preview.
    Example: `python preview.py 52.2.1`
    """, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("notesfile", help="version number of the release notes to preview")

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()


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


# Stub to make gettext work, no actual translation.
class Translation(object):
    def gettext(self, text):
        return text
    ugettext = gettext
    ngettext = gettext

notes = ReleaseNotes()
note = notes.notes.get(args.notesfile)

if not note:
    print "Error: Can't find notes for version '{0}'.".format(args.notesfile)
    sys.exit(1)

translator = Translation()

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
    o = template.render(**note)
    f.write(o.encode('utf8'))

