# -*- coding: utf-8 -*-

import argparse
import datetime
import jinja2
import markdown
import os
import sys
import time
import yaml

from loader import ReleaseNotes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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


class Handler(FileSystemEventHandler):
    def __init__(self, version):
        translator = Translation()

        self.jinja_env = jinja2.Environment(
            extensions = ["jinja2.ext.i18n"],
            loader = jinja2.FileSystemLoader(os.path.abspath('./template')),
        )
        self.jinja_env.globals.update(url=url)
        self.jinja_env.filters['markdown'] = safe_markdown
        self.jinja_env.filters['f'] = f
        self.jinja_env.filters['l10n_format_date'] = l10n_format_date
        self.jinja_env.install_gettext_translations(translator)
        self.template = self.jinja_env.get_template('release-notes.html')
        self.version = version
        self.updatetime = datetime.datetime.fromtimestamp(0)
        self.updatepreview()


    def updatepreview(self):
        notes = ReleaseNotes()
        note = notes.notes.get(self.version)
        if not note:
            print "Error: Can't find notes for version '{0}'.".format(self.version)
            sys.exit(1)
        with open("preview.html", "wb") as f:
            o = self.template.render(**note)
            f.write(o.encode('utf8'))


    def throttle_updates(self, timestamp):
        # Multiple FileModified events can fire, so only update
        # once per second.
        delta = timestamp - self.updatetime
        if delta.seconds > 0:
            self.updatepreview()
            print "{0}: Updated preview.html\n".format(timestamp.strftime("%H:%M:%S"))
            self.updatetime = datetime.datetime.now()


    def on_modified(self, event):
        self.throttle_updates(datetime.datetime.now())


handler = Handler(args.notesfile)
observer = Observer()
observer.schedule(handler, path='beta', recursive=False)
observer.schedule(handler, path='release', recursive=False)
observer.start()
print "Updating preview.html every time data is modified, press Ctrl-C to end."
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
