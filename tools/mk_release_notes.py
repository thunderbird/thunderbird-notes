#!/usr/bin/python3
"""
Generate notes for monthly release
"""

import os
import re
import sys
from pathlib import Path
from urllib.request import urlopen

import sort_notes
from tools_lib import guess_release_date, yaml, notes_template

here = os.getcwd()
beta_dir = Path(os.path.join(here, "beta"))
release_dir = Path(os.path.join(here, "release"))
beta_notes_yaml = "{this_release}beta.yml"
release_notes_yaml = "{this_release}.yml"

CUR_VERSION_URL = (
    "https://hg.mozilla.org/releases/{repo}/raw-file/tip/mail/config/version.txt"
)


def gen_notes(this_release):
    in_yaml = beta_dir / beta_notes_yaml.format(this_release=this_release)
    out_yaml = release_dir / release_notes_yaml.format(this_release=this_release)

    if out_yaml.exists():
        raise FileExistsError(out_yaml)

    print("Generating notes for Thunderbird {this_release}".format(this_release=this_release))

    release_date, human_date = guess_release_date()
    ver_major = this_release.split(".")[0]

    old_yaml = yaml.load(in_yaml)
    new_yaml = yaml.load(notes_template.TMPL_HEADER)

    new_yaml["release"]["release_date"] = release_date
    new_yaml["release"]["text"] = notes_template.TMPL_RELEASE_TEXT.format(
        ver_major=ver_major, human_date=human_date
    )
    new_yaml["release"]["import_system_requirements"] = (
        old_yaml["release"]["import_system_requirements"]
    )

    new_yaml["notes"] = []
    for tag_name in ["new", "changed", "fixed"]:
        for note in old_yaml['notes']:
            if note['tag'] == tag_name:
                if 'group' in note:
                    del note['group']
                new_yaml["notes"].append(note)

    sec_note = notes_template.TMPL_SEC_NOTE.format(
        thunderbird_version=f"thunderbird{ver_major}"
    )
    note = {'note': sec_note, 'tag': 'fixed'}
    new_yaml["notes"].append(note)

    with open(out_yaml, "w") as fp:
        yaml.dump(new_yaml, fp)

    sort_notes.sort_notes(out_yaml)

    print("Wrote notes to {}.".format(out_yaml))


def get_version():
    with urlopen(CUR_VERSION_URL.format(repo="comm-beta")) as response:
        data = response.read()
        version = data.strip().decode("utf-8")

    return version


def main():
    if len(sys.argv) > 1:
        version = sys.argv[1]
    else:
        version = get_version()

    gen_notes(version)


if __name__ == "__main__":
    main()
