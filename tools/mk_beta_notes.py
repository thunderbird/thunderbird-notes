#!/usr/bin/python3
"""
Set up notes for a beta
"""

import os
import sys
from pathlib import Path
from urllib.request import urlopen
from tools_lib import guess_release_date, yaml, notes_template

here = os.getcwd()
beta_dir = Path(os.path.join(here, "beta"))
ver_notes_yaml = "{this_beta}beta.yml"

CUR_VERSION_URL = (
    "https://hg.mozilla.org/releases/{repo}/raw-file/tip/mail/config/version.txt"
)


def gen_notes(this_beta):
    out_yaml = beta_dir / ver_notes_yaml.format(this_beta=this_beta)

    if out_yaml.exists():
        raise FileExistsError(out_yaml)

    print("Generating notes for Thunderbird {this_beta}".format(this_beta=this_beta))

    release_date, human_date = guess_release_date()
    ver_major = this_beta.split(".")[0]

    new_yaml = yaml.load(notes_template.TMPL_HEADER)
    new_yaml["release"]["text"] = notes_template.TMPL_BETA_TEXT.format(
        ver_major=ver_major, human_date=human_date
    )
    new_yaml["release"][
        "import_system_requirements"
    ] = notes_template.REQUIREMENTS_IMPORT["beta"]

    new_yaml["release"]["groups"] = [" "]

    new_yaml["release"]["release_date"] = release_date

    new_yaml["notes"] = []

    with open(out_yaml, "w") as fp:
        yaml.dump(new_yaml, fp)

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
