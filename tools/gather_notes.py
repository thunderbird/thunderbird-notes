#!/usr/bin/python
"""
Copy notes from previous beta releases to make notes for an ESR
"""

from __future__ import print_function

import sys
import os
import re
import json
from pathlib import Path
from urllib.request import urlopen
from distutils.version import StrictVersion
from collections import OrderedDict
import yaml

here = os.getcwd()
beta_dir = Path(os.path.join(here, 'beta'))
release_dir = Path(os.path.join(here, 'release'))
ver_notes_yaml = 'ver_notes.yml'

MERCURIAL_TAGS_URL = 'https://hg.mozilla.org/releases/comm-esr78/json-tags'
CHANGESET_URL_TEMPLATE = 'https://hg.mozilla.org/releases/comm-esr78/json-pushes?fromchange={from_version}&tochange={to_version}&full=1'
BUG_NUMBER_REGEX = re.compile(r'bug \d+', re.IGNORECASE)
BACKOUT_REGEX = re.compile(r'back(\s?)out|backed out|backing out', re.IGNORECASE)

class Bug:
    def __init__(self, bug_no, tag, note_text):
        self.bugs = [bug_no]
        self.tag = tag
        self.note = note_text

    def add_bug(self, bug):
        self.bugs.append(bug)

    def strip_bugs(self, fixed):
        fixed_bugs = [bug_no for bug_no in self.bugs if bug_no in fixed]
        self.bugs = fixed_bugs


def represent_dictionary_order(self, dict_data):
    return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())


def setup_yaml():
    yaml.add_representer(OrderedDict, represent_dictionary_order)


def mk_new_note(bug):
    rv_note = OrderedDict({'note': bug.note,
                           'tag': bug.tag})
    bug.bugs.sort()
    for i in range(len(bug.bugs)):
        if i == 0:
            key = 'bug'
        else:
            key = 'bug{}'.format(i + 1)
        rv_note[key] = bug.bugs[i]

    return rv_note


def load_notes(previous_esr, this_beta):
    beta_notes = {}
    new_notes = []
    rel_notes = []

    esr_major = previous_esr.split('.')[0]
    min_version = StrictVersion('{}.0.0'.format(esr_major))
    max_version = StrictVersion('{}.0'.format(this_beta))

    bug_list, backout_list = get_buglist(previous_esr)
    bugs_fixed = set.union(bug_list, backout_list)

    note_files = os.listdir(beta_dir)
    for _file in note_files:
        if not _file.endswith('beta.yml'):
            continue
        version = StrictVersion(_file[:-8])
        # Exclude the previous esr's beta and lower and anything newer than
        # the current esr
        if version < min_version:
            continue
        if version > max_version:
            continue

        with open(os.path.join(beta_dir, _file), 'r') as fp:
            doc = yaml.safe_load(fp)
            beta_notes[_file[:-8]] = doc

    versions = sorted([StrictVersion(v) for v in beta_notes.keys()])

    for ver_str in [str(v) for v in versions]:
        ver_notes = beta_notes[ver_str]['notes']
        for note in ver_notes:
            if 'bug' not in note:
                continue
            if note['tag'] == 'unresolved':
                continue

            rel_note = Bug(note['bug'], note['tag'], note['note'])

            for b in ('bug2', 'bug3', 'bug4', 'bug5', 'bug6', 'bug7', 'bug8', 'bug9'):
                if b in note:
                    rel_note.add_bug(note[b])

            new_notes.append(rel_note)

    for bug in new_notes:
        if any([b for b in bug.bugs if b in bugs_fixed]):
            for b2 in bug.bugs:
                if b2 not in bugs_fixed:
                    bug.bugs.remove(b2)
            new_note = mk_new_note(bug)
            rel_notes.append(new_note)

    setup_yaml()
    with open(ver_notes_yaml, 'w') as fp:
        yaml.dump([n for n in rel_notes if n['tag'] == 'new'], fp, default_flow_style=False)
        yaml.dump([n for n in rel_notes if n['tag'] == 'changed'], fp, default_flow_style=False)
        yaml.dump([n for n in rel_notes if n['tag'] == 'fixed'], fp, default_flow_style=False)

    # TODO: Print out bugs that were not found in the previous notes
    # TODO: If there is nothing "new" or "changed" the output has an empty list, a comment would
    #  be better.
    print('Wrote notes to {}.'.format(ver_notes_yaml))


def get_bugs_in_changeset(changeset_data):
    unique_bugs, unique_backout_bugs = set(), set()
    for data in changeset_data.values():
        for changeset in data['changesets']:
            if is_excluded_change(changeset):
                continue

            changeset_desc = changeset['desc']
            bug_re = BUG_NUMBER_REGEX.search(changeset_desc)

            if bug_re:
                bug_number = bug_re.group().split(' ')[1]

                if is_backout_bug(changeset_desc):
                    unique_backout_bugs.add(int(bug_number))
                else:
                    unique_bugs.add(int(bug_number))

    return unique_bugs, unique_backout_bugs


def is_excluded_change(changeset):
    excluded_change_keywords = [
        'a=test-only',
        'a=release',
    ]
    return any(keyword in changeset['desc'] for keyword in excluded_change_keywords)


def is_backout_bug(changeset_description):
    return bool(BACKOUT_REGEX.search(changeset_description))


def get_buglist(previous_esr):
    """Retrieve the list of bugs since the last release"""
    from_rev = None
    with urlopen(MERCURIAL_TAGS_URL) as response:
        data = json.load(response)

    e_major, e_minor, e_patch = previous_esr.split('.')
    previous_esr_tag = 'THUNDERBIRD_{}_{}_{}_RELEASE'.format(e_major, e_minor, e_patch)
    to_rev = data['node']  # Rev of tip

    for tag in data['tags'][:10]:
        if tag['tag'] == previous_esr_tag:
            print('Using tag {} at rev {}.'.format(tag['tag'], tag['node']))
            from_rev = tag['node']
            break
        else:
            continue

    if from_rev is None:
        raise Exception('Did not find a RELEASE tag in the first 10 tags')

    changeset_url = CHANGESET_URL_TEMPLATE.format(from_version=from_rev, to_version=to_rev)
    with urlopen(changeset_url) as response:
        data = json.load(response)
    unique_bugs, unique_backout_bugs = get_bugs_in_changeset(data)

    print('Fixed bugs:')
    print(' '.join([str(bug) for bug in unique_bugs]))
    print('Backout bugs:')
    print(' '.join([str(bug) for bug in unique_backout_bugs]))
    return unique_bugs, unique_backout_bugs


if __name__ == '__main__':
    try:
        previous_esr = sys.argv[1]
        this_beta = sys.argv[2]
    except IndexError:
        print("Usage: {} previous_esr current_beta".format(sys.argv[0]))
        print("Example: ./tools/gather_notes.py 78.4.3 84")
        print("")
        sys.exit(1)

    load_notes(previous_esr, this_beta)
