#!/usr/bin/python3
"""
Updates the YAML files for each release replacing bug: bug2: bug3: etc
with a list structure instead.

This script was written for Python 3.9, though it should run on >= 3.6

The only external requirement is ruamel.yaml==0.16.12
ruamel.yaml was chosen over PyYAML as it has built in functionality to
preserve comments and whitespace aka "round-trip" editing.

Running:
Run from root of a thunderbird-notes checkout. The script checks for a
"new" directory in the root and will silently remove it if one exists.

The existing YAML files are not modified by this script, the ["release",
"beta", "archive"] structure is recreated under new/ and the output is
written there. After verifying the output, the new files can be copied
(not moved!) over the old files.

```
 cp -av new/* .
```

The new directory will not have every YAML file! There are several
releases especially in archive that do not have any bug numbers. Those
files are not written to new to make verification a little easier.

Verification:
I have not personally inspected every YAML file that this script outputs.
I have checked about 25% of them. It's possible that some will be
formatted oddly after being updated.

I have run a website build with the modified files. That resulted in
no changes to the rendered HTML.
"""

import os
import shutil

from ruamel.yaml import YAML

yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.unicode_supplementary = False
yaml.preserve_quotes = True
yaml.width = 85


def update_notes_file(path, new_path, notes_file):
    changed_flag = False
    if notes_file.endswith(".yml"):
        notes_path = os.path.join(path, notes_file)
        with open(notes_path, "r") as f:
            doc = yaml.load(f)

        for note in doc['notes']:
            bugs = [int(bug) for k, bug in note.items() if k.startswith("bug")]
            bug_keys = [k for k in note.keys() if k.startswith("bug")]

            if bugs:
                changed_flag = True

                # To preserve formatting as much as possible, place the new list
                # within the OrderedDict right before "bug".
                bug_pos = list(note.keys()).index("bug")
                note.insert(bug_pos, "bugs", yaml.seq(bugs))

                # Move any comments associated with the bug number lines.
                # This includes blank lines that may be present after
                for bug_key in bug_keys:
                    if bug_key in note.ca.items:
                        # bug -> 0, bug2 -> 1, bug3 -> 2...
                        if bug_key == "bug":
                            bug_index = 0
                        else:
                            # This may produce a ValueError if there's any bad
                            # YAML left.
                            bug_index = int(bug_key[-1]) - 1

                        # This is an internal ruamel.yaml comment structure.
                        # It's mostly meant to grab any blank lines when the bug number(s)
                        # are positioned last in the note structure within the YAML
                        note["bugs"].ca.items[bug_index] = [note.ca.items[bug_key][2], None, None, None]

                    # Remove the old bug bug2 bug3 keys, leaving bugs in the same place
                    del note[bug_key]

        if changed_flag:
            new_file = os.path.join(new_path, notes_file)

            with open(new_file, 'w') as fp:
                yaml.dump(doc, fp)


def main():
    notes_dirs = [
        'release',
        'beta',
        'archive',
    ]

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    new_notes_base = os.path.join(base_path, "new")
    try:
        shutil.rmtree(new_notes_base)
    except FileNotFoundError:
        pass
    os.mkdir(new_notes_base)

    for notes_dir in notes_dirs:
        path = os.path.join(base_path, notes_dir)
        new_path = os.path.join(new_notes_base, notes_dir)
        os.mkdir(new_path)
        notes_files = os.listdir(path)
        for notes_file in notes_files:
            update_notes_file(path, new_path, notes_file)


if __name__ == "__main__":
    main()
