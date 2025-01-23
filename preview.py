# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import datetime
import pathlib

import jinja2
import markupsafe
import markdown
import os
import sys
import time

import requests

from loader import notes_dirs
from loader import ReleaseNotes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

TEMPLATE_DOWNLOAD_URL = 'https://raw.githubusercontent.com/thunderbird/thunderbird-website/master/sites/www.thunderbird.net'
THUNDERBIRD_URL = 'https://www.thunderbird.net'
TEMPLATE_OUT_DIR = '_template'

parser = argparse.ArgumentParser(
    description="""
    Enter the version number you want to preview.
    Example: `python preview.py 52.2.1`
    """, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("notesfile", help="version number of the release notes to preview")
parser.add_argument("-r", "--refresh_template", help="whether to download the template from the thunderbird-website repo", action='store_true')
parser.add_argument("-s", "--simple_html", help="use simplified html output", action="store_true")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

is_email = False
if "email" in sys.argv:
    is_email = True
    sys.argv.remove("email")

args = parser.parse_args()


def download_template():
    """Downloads the required templates from the thunderbird-website repo"""
    base_url = TEMPLATE_DOWNLOAD_URL
    files = ('includes/base/base.html',
             'includes/base/footer.html',
             'includes/base/nav.html',
             'includes/base/page.html',
             'includes/components/page-separator-cover.html',
             'includes/_enonly/release-notes.html',
             'includes/release-notes-feed.html')

    print("Downloading latest templates from thunderbird-website")

    for file in files:
        print(f'{base_url}/{file}')
        response = requests.get(f'{base_url}/{file}')
        response.raise_for_status()

        out_file = pathlib.Path(file)
        if file.endswith('release-notes.html'):
            out_file = out_file.name
        out_path = pathlib.Path(TEMPLATE_OUT_DIR) / out_file

        # Ensure we have the folder
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, 'wb') as fh:
            fh.write(response.content)

    print("Finished downloading latest templates")


def stub_templates():
    """Stubs some template includes out that we don't really need"""
    files = ('includes/donation-includes.html',
             'includes/lang_switcher.html')

    for file in files:
        # Ensure we have the folder
        pathlib.Path(f'{TEMPLATE_OUT_DIR}/{file}').parent.mkdir(parents=True, exist_ok=True)

        with open(f'{TEMPLATE_OUT_DIR}/{file}', 'w') as fh:
            fh.write('')


def safe_markdown(text):
    if not text:
        text = ''
    return markupsafe.Markup(markdown.markdown(text))


def l10n_format_date(text):
    return text


def url(*args, **kwargs):
    return ''


def donate_url(*args, **kwargs):
    return ''


def svg(name, *args, **kwargs):
    return f'<img src="{THUNDERBIRD_URL}/media/svg/{name}.svg">'


def static(filepath):
    return f'{THUNDERBIRD_URL}/media/{filepath}'


def l10n_css(*args, **kwargs):
    return ''


def download_thunderbird(*args, **kwargs):
    return ''


def thunderbird_url(*args, **kwargs):
    return ''


def is_system_requirements_dict(*args, **kwargs):
    return False


def f(s, *args, **kwargs):
    return s.format(*args, **kwargs)


# Stub to make gettext work, no actual translation.
class Translation(object):
    def gettext(self, text):
        return text
    ugettext = gettext
    ngettext = gettext

def get_latest_build(default_channel):
    return

def get_channels():
    return {}

def get_mobile_platforms():
    return {}


class Handler(FileSystemEventHandler):
    def __init__(self, version, preview_template):
        translator = Translation()

        self.jinja_env = jinja2.Environment(
            extensions=["jinja2.ext.i18n"],
            loader=jinja2.FileSystemLoader(os.path.abspath(f'./{TEMPLATE_OUT_DIR}')),
        )
        self.jinja_env.globals.update(url=url)
        self.jinja_env.globals.update(svg=svg)
        self.jinja_env.globals.update(static=static)
        self.jinja_env.globals.update(l10n_css=l10n_css)
        self.jinja_env.globals.update(download_thunderbird=download_thunderbird)
        self.jinja_env.globals.update(thunderbird_url=thunderbird_url)
        self.jinja_env.globals.update(donate_url=donate_url)
        self.jinja_env.globals.update(is_system_requirements_dict=is_system_requirements_dict)
        self.jinja_env.globals.update(NOW=datetime.datetime.now())
        self.jinja_env.globals.update(settings={'FRU_FORM_IDS': {'support': 'support'}})
        self.jinja_env.globals.update(override_nav_donate_form_id="")
        self.jinja_env.globals.update(get_latest_build=get_latest_build)
        self.jinja_env.globals.update(get_channels=get_channels)
        self.jinja_env.globals.update(get_mobile_platforms=get_mobile_platforms)
        self.jinja_env.globals.update(default_channel='release')
        self.jinja_env.filters['markdown'] = safe_markdown
        self.jinja_env.filters['f'] = f
        self.jinja_env.filters['l10n_format_date'] = l10n_format_date
        self.jinja_env.install_gettext_translations(translator)
        self.jinja_env.trim_blocks = True
        self.jinja_env.lstrip_blocks = True
        self.template = self.jinja_env.get_template(preview_template)
        self.version = version
        self.updatetime = datetime.datetime.fromtimestamp(0)
        self.updatepreview()

    def updatepreview(self):
        notes = ReleaseNotes()
        note = notes.notes.get(self.version)
        if not note:
            print("Error: Can't find notes for version '{0}'.".format(self.version))
            sys.exit(1)
        with open("preview.html", "wb") as f:
            o = self.template.render(is_preview=True, **note)
            f.write(o.encode('utf8'))

    def throttle_updates(self, timestamp):
        # Multiple FileModified events can fire, so only update
        # once per second.
        delta = timestamp - self.updatetime
        if delta.seconds > 0:
            self.updatepreview()
            print("{0}: Updated preview.html\n".format(timestamp.strftime("%H:%M:%S")))
            self.updatetime = datetime.datetime.now()

    def on_modified(self, event):
        self.throttle_updates(datetime.datetime.now())




if args.refresh_template or not pathlib.Path('_template/release-notes.html').exists():
    download_template()
    stub_templates()

preview_template = pathlib.Path('_template/release-notes.html')
if args.simple_html or is_email:
    preview_template = pathlib.Path("simple_html.html")

handler = Handler(args.notesfile, preview_template.name)
observer = Observer()
for notedir in notes_dirs:
    observer.schedule(handler, path=notedir, recursive=False)
observer.start()

if is_email:
    observer.stop()
else:
    print("Updating preview.html every time data is modified, press Ctrl-C to end.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

observer.join()
