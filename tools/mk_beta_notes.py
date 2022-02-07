#!/usr/bin/python3
"""
Set up notes for a beta
"""

import sys
import os
import re
import json
from pathlib import Path
from urllib.request import urlopen
from distutils.version import StrictVersion
from datetime import date, timedelta
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq as CS

from tools_lib import notes_template

yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.unicode_supplementary = False
yaml.preserve_quotes = True
yaml.width = 85

here = os.getcwd()
beta_dir = Path(os.path.join(here, "beta"))
ver_notes_yaml = "{this_beta}beta.yml"

CUR_VERSION_URL = "https://hg.mozilla.org/releases/{repo}/raw-file/tip/mail/config/version.txt"


def gen_notes(this_beta):
    print("Generating notes for Thunderbird {this_beta}".format(this_beta=this_beta))

    release_date, human_date = guess_release_date()
    ver_major = this_beta.split(".")[0]

    new_yaml = yaml.load(notes_template.TMPL_HEADER)
    new_yaml["release"]["text"] = notes_template.TMPL_BETA_TEXT.format(ver_major=ver_major, human_date=human_date)
    new_yaml["release"]["import_system_requirements"] = notes_template.REQUIREMENTS_IMPORT["beta"]

    new_yaml["release"]["release_date"] = release_date

    new_yaml["notes"] = []

    out_yaml = ver_notes_yaml.format(this_beta=this_beta)
    with open(out_yaml, "w") as fp:
        yaml.dump(new_yaml, fp)
        
    print("Wrote notes to {}.".format(out_yaml))


def guess_release_date():
    today = date.today()
    guess = today + timedelta(days=2)
    if guess.weekday() == 5:  # Saturday
        guess = guess + timedelta(days=2)  # Shift to Monday
    if guess.weekday() == 6:  # Sunday
        guess = guess + timedelta(days=1)  # Shift to Monday
    assert guess.weekday() < 5

    human_date = guess.strftime("%B %e, %Y")

    return guess.isoformat(), human_date


def get_version():
    with urlopen(CUR_VERSION_URL.format(repo="comm-beta")) as response:
        data = response.read()
        version = data.strip().decode("utf-8")

    return version


def main():
    version = get_version()

    gen_notes(version)


if __name__ == "__main__":
    main()
