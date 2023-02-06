#!/usr/bin/python3
"""
Copy notes from previous beta releases to make notes for an ESR
"""

import argparse
import os
import re
import json
from pathlib import Path
from urllib.request import urlopen
from packaging.version import Version
from datetime import date, timedelta

from tools_lib import yaml, notes_template
from ruamel.yaml.comments import CommentedSeq as CS


topdir = Path(os.path.dirname(__file__)) / ".."
beta_dir = Path(os.path.join(topdir, "beta"))
release_dir = Path(os.path.join(topdir, "release"))
ver_notes_yaml = "{this_esr}.yml"

MERCURIAL_TAGS_URL = "https://hg.mozilla.org/releases/comm-esr{major}/json-tags"
RELEASE_TAG_RE = re.compile(r"THUNDERBIRD_([\d_b]+)_RELEASE")
CHANGESET_URL_TEMPLATE = "https://hg.mozilla.org/releases/comm-esr102/json-pushes?fromchange={from_version}&tochange={to_version}&full=1"
BUG_NUMBER_REGEX = re.compile(r"bug \d+", re.IGNORECASE)
BACKOUT_REGEX = re.compile(r"back(\s?)out|backed out|backing out", re.IGNORECASE)

PD_VERSIONS = "https://product-details.mozilla.org/1.0/thunderbird_versions.json"
CUR_VERSION_URL = "https://hg.mozilla.org/releases/{repo}/raw-file/{rev}/mail/config/version.txt"

ESR_VERSIONS = ("102", "115")


class RelNote:
    def __init__(self, bugs, tag, note_text):
        bugs.sort()
        self.bugs = bugs
        self.tag = tag
        self.note = note_text

    @property
    def output(self):
        return {"note": self.note,
                "tag": self.tag,
                "bugs": self.bugs}


def load_notes(this_esr, previous_esr, previous_esr_rev):
    beta_notes = {}
    new_notes = []
    rel_notes = []

    esr_major = previous_esr.split(".")[0]
    min_version = Version("{}.0.0".format(esr_major))

    print("""Generating notes for Thunderbird {this_esr}
Previous esr: {previous_esr}
    """.format(this_esr=this_esr, previous_esr=previous_esr, min_version=min_version))

    bug_list, backout_list = get_buglist(previous_esr_rev)
    bugs_fixed = set.union(bug_list, backout_list)

    note_files = os.listdir(str(beta_dir))
    for _file in note_files:
        if not _file.endswith("beta.yml"):
            continue
        version = Version(_file[:-8])
        # Exclude versions lower than the beta for the previous esr
        # anything newer than the current beta
        if version < min_version:
            continue

        with open(os.path.join(beta_dir, _file), "r") as fp:
            doc = yaml.load(fp)
            beta_notes[_file[:-8]] = doc

    versions = sorted([Version(v) for v in beta_notes.keys()])

    for ver_str in [str(v) for v in versions]:
        ver_notes = beta_notes[ver_str]["notes"]
        for note in ver_notes:
            if "bugs" not in note:
                continue
            if note["tag"] == "unresolved":
                continue

            rel_note = RelNote(note["bugs"], note["tag"], note["note"])

            new_notes.append(rel_note)

    noted_bugs = set()
    for note in new_notes:
        # Only add this note if it is for bugs that are new/changed/fixed in this release
        if any([b for b in note.bugs if b in bugs_fixed]):
            # Remove references to other bugs that might be on the note
            for b2 in note.bugs:
                if b2 not in bugs_fixed:
                    note.bugs.remove(b2)
                else:
                    noted_bugs.add(b2)
            rel_notes.append(note.output)

    new_yaml = yaml.load(notes_template.TMPL_HEADER)
    new_yaml["release"]["text"] = notes_template.TMPL_RELEASE_TEXT
    new_yaml["release"]["import_system_requirements"] = notes_template.REQUIREMENTS_IMPORT["release"]
    new_yaml["release"]["release_date"] = guess_release_date()

    notes_sequence = CS()
    note_counter = 0
    for tag_name in ["new", "changed", "fixed"]:
        tag_notes = [n for n in rel_notes if n["tag"] == tag_name]
        if tag_notes:
            notes_sequence.extend(tag_notes)
            notes_sequence.yaml_set_comment_before_after_key(note_counter, "{}\n".format(tag_name.capitalize()), 2)
            note_counter += len(tag_notes)
    new_yaml["notes"] = notes_sequence

    out_yaml = ver_notes_yaml.format(this_esr=this_esr)
    with open(release_dir / out_yaml, "w") as fp:
        yaml.dump(new_yaml, fp)
        
    print("Wrote notes to {}.".format(out_yaml))

    no_note_bugs = sorted(bugs_fixed - noted_bugs)
    if no_note_bugs:
        # Print out bugs where no note is available
        print("")
        print("Bugs that do not have an associated note:")

        bugzilla_url = "https://bugzilla.mozilla.org/rest/bug?include_fields=id,summary&id={}".format(
            ",".join([str(b) for b in no_note_bugs]))
        with urlopen(bugzilla_url) as response:
            data = json.load(response)

        for note in data["bugs"]:
            print("{} - {}".format(note["id"], note["summary"]))


def get_bugs_in_changeset(changeset_data):
    unique_bugs, unique_backout_bugs = set(), set()
    for data in changeset_data.values():
        for changeset in data["changesets"]:
            if is_excluded_change(changeset):
                continue

            changeset_desc = changeset["desc"]
            bug_re = BUG_NUMBER_REGEX.search(changeset_desc)

            if bug_re:
                bug_number = bug_re.group().split(" ")[1]

                if is_backout_bug(changeset_desc):
                    unique_backout_bugs.add(int(bug_number))
                else:
                    unique_bugs.add(int(bug_number))

    return unique_bugs, unique_backout_bugs


def is_excluded_change(changeset):
    excluded_change_keywords = [
        "a=test-only",
        "a=release",
    ]
    return any(keyword in changeset["desc"] for keyword in excluded_change_keywords)


def is_backout_bug(changeset_description):
    return bool(BACKOUT_REGEX.search(changeset_description))


def get_buglist(from_rev):
    """Retrieve the list of bugs since the last release"""
    to_rev = "tip"
    changeset_url = CHANGESET_URL_TEMPLATE.format(from_version=from_rev, to_version=to_rev)
    with urlopen(changeset_url) as response:
        data = json.load(response)
    unique_bugs, unique_backout_bugs = get_bugs_in_changeset(data)

    if unique_bugs:
        print("Fixed bugs:")
        print(" ".join([str(bug) for bug in sorted(unique_bugs)]))
        print("")
    if unique_backout_bugs:
        print("Backout bugs:")
        print(" ".join([str(bug) for bug in sorted(unique_backout_bugs)]))

    return unique_bugs, unique_backout_bugs


def guess_release_date():
    today = date.today()
    guess = today + timedelta(days=2)
    if guess.weekday() == 5:  # Saturday
        guess = guess + timedelta(days=2)  # Shift to Monday
    if guess.weekday() == 6:  # Sunday
        guess = guess + timedelta(days=1)  # Shift to Monday
    assert guess.weekday() < 5

    return guess.isoformat()


def fetch(url, data_type="text"):
    with urlopen(url) as response:
        if data_type == "json":
            data = json.load(response)
        else:
            data = response.read().strip().decode("utf-8")
    return data


def get_prev_release_rev(tags):
    for tag in tags[:10]:
        match = RELEASE_TAG_RE.match(tag["tag"])
        if match:
            print("Using tag {} at rev {}.".format(tag["tag"], tag["node"]))
            return tag["node"]
    raise Exception("Did not find a RELEASE tag in the first 10 tags")


def get_version_from_rev(repo, rev):
    return fetch(CUR_VERSION_URL.format(repo=repo, rev=rev))


def get_versions(major_version):
    versions = {}

    esr_tags = fetch(MERCURIAL_TAGS_URL.format(major=major_version), data_type="json")
    prev_esr_rev = get_prev_release_rev(esr_tags["tags"])
    versions["prev_esr_rev"] = prev_esr_rev
    prev_esr_version = get_version_from_rev(f"comm-esr{major_version}", prev_esr_rev)
    versions["previous_esr"] = prev_esr_version

    this_esr_version = get_version_from_rev(f"comm-esr{major_version}", "tip")
    versions["this_esr"] = this_esr_version

    return versions


def main():
    parser = argparse.ArgumentParser(description="Make ESR notes")
    parser.add_argument("major_ver", metavar="major_version", choices=ESR_VERSIONS, help="Major ESR version")
    args = parser.parse_args()

    versions = get_versions(args.major_ver)

    load_notes(versions["this_esr"], versions["previous_esr"], versions["prev_esr_rev"])


if __name__ == "__main__":
    main()
