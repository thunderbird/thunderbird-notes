# Release Notes Tools

## Requirements

The scripts in this directory have been written for Python 3 and have
additional requirements that need to be installed (tools/requirements.txt).

## Scripts

### major_esr_notes.py

**Usage:** `./tools/major_esr_notes.py <previous esr> <new esr>`

**Example:** `./tools/major_esr_notes.py 91 102`

When a new major version of Thunderbird is released, such as Thunderbird
102.0.0, the release notes include everything from the beta releases over
the past year excluding bugs that were uplifted to the old stable release.

`major_esr_notes.py` will produce a YAML file that's a decent starting
point. The header will come from `tools_lib/notes_template.py:TMPL_RELEASE_TEXT`.
For a new major version, replace `import_system_requirements` will a full
`system_requirements` field. The requirements themselves are based on
what [Firefox publishes](https://www.mozilla.org/en-US/firefox/102.0a1/system-requirements/).

The notes file will be written to the repository root and needs to be
reviewed and cleaned up prior to publishing. The `sort_notes` script can
help with that task.

### mk_esr_notes.py

**Usage:** `./tools/mk_esr_notes.py`

**Example:** `./tools/mk_esr_notes.py`

This script will generate a YAML file for an upcoming stable/esr release.
It needs to run after all uplifts have been pushed to the release repository.

The output will need to be reviewed and the notes themselves need to be
sorted properly. (`sort_notes.py` can probably help.)

The script will retrieve bug numbers from Mercurial and then look up notes
in beta notes files. Any bugs that were not found in a beta are looked up
in Bugzilla and printed to the console for review. Backouts are called out
as they could be relevant as well.

### mk_beta_notes.py

Similar to `mk_esr_notes.py` except that the "notes" object is empty. There's
no automatic way to produce beta notes unfortunately.

### sort_notes.py

**Usage:** `./tools/sort_notes.py <yaml_file>`

**Example:** `./tools/sort_notes.py 102.0.yml`

Reviewing and cleaning up the output of `major_esr_notes.py` for major version
release is not fun. The notes in the produced file are jumbled up in no
particular order.

`sort_notes` will read yaml file produced by `major_esr_notes` and rearrange
the notes into something that's hopefully less burdensome to clean up for
publishing.

It works by extracting bug numbers from the provided file and querying
Bugzilla for the Product and Categories. Product and Category are combined
and a weight is assigned. Then for each note tag (new, changed, fixed), the
notes are sorted based on weight.

Output is written to "sorted.yml".

### yamlfmt.py

**Usage:** `./tools/yamlfmt.py <yaml_file> [-w]`

**Example:** `./tools/yamlfmt.py release/102.0.yml [-w]`

Formats a YAML file consistently enough that yamllint should not complain
too much.

The optional `-w` argument will write the output back to the same file. Omit
it to write to stdout.

## Obsolete Scripts

### bug_fixer.py
This script was used to convert bug number fields from "bug, bug2, bug3"
to the "bugs" field that's now in use. There's no reason to run it ever
again and is kept for historical reference. 

