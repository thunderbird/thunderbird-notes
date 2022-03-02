#!/usr/bin/python

from __future__ import print_function

import sys
import os

from pathlib import Path
from packaging.version import Version
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq as CS

from tools_lib import notes_template

yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.unicode_supplementary = False
yaml.preserve_quotes = True
yaml.width = 85

here = os.path.dirname(__file__)
beta_dir = Path(os.path.join(here, "..", "beta"))
release_dir = Path(os.path.join(here, "..", "release"))
ver_notes_yaml = "{this_esr}.yml"


"""
There are some gremlins lurking in this script, but it gets most of the work done.

This is for generating release notes for a new major ESR-based release (aka 91.0).

Notes will need to be rearranged into the proper order. They also need to be checked
to make sure that they actually apply. For example, for ESR91, regression fixes that
were caused by the change to js-smtp/js-mime and such are not included.
"""


class RelNote:
    def __init__(self, bugs, tag, note_text):
        bugs.sort()
        self.bugs = bugs
        self.tag = tag
        self.note = note_text

    @property
    def output(self):
        return {"note": self.note, "tag": self.tag, "bugs": self.bugs}


def load_notes(previous, current):
    uplift_bugs = []
    beta_notes = {}
    new_notes = []

    min_version = Version("{}.0".format(previous))
    max_version = Version("{}.0".format(current))

    # Get the list of bugs that were uplifted during the previous cycle.
    previous_glob = "{}.*.yml".format(previous)
    previous_notes_files = list(release_dir.glob(previous_glob))
    for _file in previous_notes_files:
        with _file.open() as fp:
            doc = yaml.load(fp)

        ver_notes = doc["notes"]
        for note in ver_notes:
            if note["tag"] == "unresolved":
                continue
            if "bugs" not in note:
                continue
            else:
                uplift_bugs.extend(note["bugs"])

    note_files = os.listdir(beta_dir)
    for _file in note_files:
        if not _file.endswith("beta.yml"):
            continue
        version = Version(_file[:-8])
        # Exclude the previous esr's beta and lower and anything newer than
        # the current esr
        if version <= min_version:
            continue
        if version > max_version:
            continue

        with open(os.path.join(beta_dir, _file), "r") as fp:
            doc = yaml.load(fp)
            beta_notes[_file[:-8]] = doc

    versions = sorted([Version(v) for v in beta_notes.keys()])

    for ver_str in [str(v) for v in versions]:
        ver_notes = beta_notes[ver_str]["notes"]
        for note in ver_notes:
            if note["tag"] == "unresolved":
                continue
            if "bugs" not in note:
                continue

            # Exclude anything that looks like it was uplifted
            if not any(elem in uplift_bugs for elem in note["bugs"]):
                rel_note = RelNote(note["bugs"], note["tag"], note["note"])
                new_notes.append(rel_note)

    new_yaml = yaml.load(notes_template.TMPL_HEADER)
    new_yaml["release"]["text"] = notes_template.TMPL_RELEASE_TEXT
    new_yaml["release"][
        "import_system_requirements"
    ] = notes_template.REQUIREMENTS_IMPORT["release"]
    new_yaml["release"]["release_date"] = "2021-08-11"

    notes_sequence = CS()
    note_counter = 0

    for tag_name in ["new", "changed", "fixed"]:
        tag_notes = [note for note in new_notes if note.tag == tag_name]
        for note in tag_notes:
            notes_sequence.append(note.output)
            notes_sequence.yaml_set_comment_before_after_key(
                note_counter, "{}\n".format(tag_name.capitalize()), 2
            )
            note_counter += len(tag_notes)

    new_yaml["notes"] = notes_sequence

    this_esr = "{}.0".format(current)
    out_yaml = ver_notes_yaml.format(this_esr=this_esr)
    with open(out_yaml, "w") as fp:
        yaml.dump(new_yaml, fp)

    print("Wrote notes to {}.".format(out_yaml))


if __name__ == "__main__":
    previous_esr = sys.argv[1]
    current_esr = sys.argv[2]
    load_notes(previous_esr, current_esr)
