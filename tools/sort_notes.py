#!/usr/bin/python

import sys
import os

from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq as CS
import requests


yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.unicode_supplementary = False
yaml.preserve_quotes = True
yaml.width = 85


here = os.path.dirname(__file__)
release_dir = Path(os.path.join(here, "..", "release"))
ver_notes_yaml = "{version}.yml"

BUG_URL = "https://bugzilla.mozilla.org/rest/bug?id={bug_nums}&include_fields=id,product,component"

COMPONENTS = {
  "Thunderbird: General": 100,
  "MailNews Core: General": 200,
  "Thunderbird: Mail Window Front End": 300,
  "Thunderbird: Message Reader UI": 400,
  "Thunderbird: Folder and Message Lists": 500,
  "Thunderbird: Toolbars and Tabs": 600,
  "MailNews Core: Security: OpenPGP": 700,
  "MailNews Core: Security: S/MIME": 800,
  "Thunderbird: Search": 900,
  "MailNews Core: Search": 1000,
  "Thunderbird: Message Compose Window": 1100,
  "MailNews Core: Composition": 1200,
  "MailNews Core: Attachments": 1300,
  "Thunderbird: Preferences": 1400,
  "Thunderbird: Account Manager": 1500,
  "MailNews Core: Account Manager": 1600,
  "Thunderbird: Filters": 1700,
  "MailNews Core: Filters": 1800,
  "Thunderbird: Migration": 1900,
  "MailNews Core: Profile Migration": 2000,
  "MailNews Core: Import": 2100,
  "Thunderbird: Add-Ons": 2200,
  "Thunderbird: FileLink": 2300,
  "Thunderbird: Address Book": 2400,
  "MailNews Core: Address Book": 2500,
  "MailNews Core: LDAP Integration": 2600,
  "Thunderbird: OS Integration": 2700,
  "Thunderbird: Installer": 2800,
  "Thunderbird: Theme": 2900,
  "Thunderbird: Disability Access": 3000,
  "MailNews Core: Backend": 3100,
  "MailNews Core: MIME": 3200,
  "MailNews Core: Database": 3300,
  "MailNews Core: Networking": 3400,
  "Thunderbird: Instant Messaging": 3500,
  "Chat Core: General": 3600,
  "Chat Core: IRC": 3700,
  "Chat Core: XMPP": 3800,
  "Chat Core: Matrix": 3900,
  "Chat Core:": 4000,
  "Thunderbird:": 4100,
  "MailNews Core:": 4200,
  "Calendar: General": 4300,
  "Calendar: Calendar Frontend": 4400,
  "Calendar: Dialogs": 4500,
  "Calendar: Tasks": 4600,
  "Calendar: E-mail based Scheduling (iTIP/iMIP)": 4700,
  "Calendar: Alarms": 4800,
  "Calendar: Import and Export": 4900,
  "Calendar: Provider:": 5000,
  "Calendar: Internal Components": 5100,
  "Calendar: ICAL.js Integration": 5200,
  "Calendar:": 5300
}


def component_weight(component):
    weight = COMPONENTS.get(component, None)
    if weight:
        return weight
    else:
        for key in COMPONENTS.keys():
            if component.startswith(key):
                return COMPONENTS[key]
    return 9999999


def component_str(product, component):
    return "{}: {}".format(product, component)


def get_components(bug_nums):
    url = BUG_URL.format(bug_nums=",".join([str(b) for b in bug_nums]))
    res = requests.get(url)
    data = res.json()
    return dict([(b["id"], component_str(b["product"], b["component"])) for b in data["bugs"]])


def get_bug_weights(bugs):
    bug_weight_map = {}
    bug_components = get_components(bugs)
    for bug_id in bug_components.keys():
        weight = component_weight(bug_components[bug_id])
        bug_weight_map[bug_id] = weight
    return bug_weight_map


def weight(note):
    return note["weight"]


def sort_notes(orig_yaml_file):
    with open(orig_yaml_file) as fp:
        doc = yaml.load(fp)

    notes = doc["notes"]

    bugs = [n.get("bugs", ["0"])[0] for n in notes]
    bug_weight_map = get_bug_weights(bugs)

    for note in notes:
        bug_nums = note.get("bugs", [])
        if bug_nums:
            bug_num = bug_nums[0]
            note["weight"] = bug_weight_map[bug_num]
        else:
            note["weight"] = 9999999

    new_notes = [n for n in notes if n.get("tag") == "new"]
    new_notes.sort(key=weight)

    changed_notes = [n for n in notes if n.get("tag") == "changed"]
    changed_notes.sort(key=weight)

    fixed_notes = [n for n in notes if n.get("tag") == "fixed"]
    fixed_notes.sort(key=weight)

    notes_seq = CS()
    note_counter = 0
    for tag_name, notes_tagged in [("new", new_notes), ("changed", changed_notes), ("fixed", fixed_notes)]:
        notes_seq.extend(notes_tagged)
        notes_seq.yaml_set_comment_before_after_key(note_counter, "{}\n".format(tag_name.capitalize()), 2)
        note_counter += len(notes_tagged)

    doc["notes"] = notes_seq

    print("Writing sorted notes file to sorted.yml.")
    with open("sorted.yml", "w") as fp:
        yaml.dump(doc, fp)


if __name__ == "__main__":
    yaml_file = sys.argv[1]
    sort_notes(yaml_file)
