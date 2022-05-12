# Thunderbird Release Notes

This repo contains release notes for Thunderbird, as displayed on [thunderbird.net](https://stage.thunderbird.net/en-US/thunderbird/releases/).
Notes are in a [YAML format](https://learnxinyminutes.com/docs/yaml/), with release versions under the 'release' directory and beta versions in the 'beta' directory.

To aid in editing these notes, you can preview changes to any of the .yml files with preview.py:

```
pip install -r requirements.txt
python preview.py 52.0
```
Once you start `preview.py` for a particular version, it will load that file and produce a `preview.html` file that you can load locally.
Any time you modify one of the release notes files, `preview.html` will be automatically refreshed with the changes, so you can just refresh
it in your browser to see your changes.

# YAML format

The format is relatively simple. There are two primary data structures, the `release` dictionary and the `notes` list.

**All strings are parsed for [Markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) for formatting.**

## Release Dictionary

```YAML
release:
  release_date: 2017-07-15
  text: |
    **System Requirements:
    • Window: Windows XP, Windows Server 2003 or later
    • Mac: Mac OS X 10.9 or later
    • Linux: GTK+ 3.4 or higher**
    Details [here](https://thunderbird.net/en-US/thunderbird/52.0/system-requirements/).

    **Please refer to [Release Notes for version 52.0](https://thunderbird.net/en-US/thunderbird/52.0/releasenotes/) to see the list of improvements and fixed issues.**
  bug_search_url: https://bugzilla.mozilla.org/buglist.cgi?o1=equals&v1=54%2B&f1=cf_tracking_thunderbird_esr52&query_format=advanced&list_id=13634735
  system_requirements:
  import_system_requirements: "52.0"
  groups:
  -
  - "Beta 2"
```

* Filename: The file name is imported as the release's version number, so **52.0** is `52.0.yml` and so on.
* `release_date`: The date of the release. If you don't specify this, the site will pull the date from product-details. Date format is YYYY-MM-DD.
* `text`: Release text that appears at the top of the notes.
* `bug_search_url`: Bugzilla URL that is linked to "complete list of changes" at the top of the notes.
* `system_requirements`: Text field for system requirements, that appears in the /system-requirements/ directory on the website for each version.
* `import_system_requirements`: Version string to import system requirements from, to avoid copy pasting sysreqs for minor versions.
* `groups`: This can be used to add subheadings to the Known Issues list. Groups are numbered starting from 1, to n. Usually the first group is unlabeled.

**Important: To ensure the YAML loader imports version numbers as strings, they should always be quoted like `"52.0"`.

## Notes List

```YAML
notes:
  - note: Problems with Gmail (folders not showing, repeated email download, etc.) introduced in version 52.2.0.
    tag: fixed
    bugs: [1234567]
    group: 2

  - note: >
      On Windows, "Send to > Mail recipient" does not work.
      Workaround: Install the [Microsoft Visual Studio 2015 redistributable runtime library](https://www.microsoft.com/en-us/download/details.aspx?id=53587)
      or the [Universal C Runtime for Windows Server](https://support.microsoft.com/en-us/help/2999226/update-for-universal-c-runtime-in-windows).
    tag: unresolved

  - note: Multiple requests for master password when GMail OAuth2 is enabled.
    tag: unresolved`
```
* `notes`: Is a list containing every note in the file. **Order is preserved on the final HTML output.**
* `note`: This is a string containing the note.
* `tag`: This is the tag defining the image that will appear next to the note. Options are:
    * new
    * changed
    * fixed
    * unresolved: This will appear in a separate "Known Issues" list.
* `bugs`: This is a list of bug numbers associated with the note. They appear on Beta release notes and when using the preview script.
* `group`: This is optional. If added, it will associate the note with the subheading in the "groups" list in the Release dictionary. Notes with no group set always go in the first unlabeled section of Known Issues. Groups are currently ignored in the Unresolved Issues.

Each string variable in the YAML file can be defined with quotes, without quotes, or using the two text block operators `>` and `|`.
* Quotes: Only needed if a control character is in the string, or to ensure a scalar is imported as a string, not a floating point or other data type.
* `>` operator: All following single-indented lines are part of the text, but **single newlines are replaced by a space, and blank lines are converted to a newline character**. More than one level of indentation is preserved.
* `|` operator: All following single-indented lines are part of the text, but **all white space is preserved**.
* Control Characters: :, {, }, [, ], ,, &, *, #, ?, |, -, <, >, =, !, %, @, `

# Getting notes on the website

Like our other sites, the `master` branch pushes to staging at https://stage.thunderbird.net and the `prod` branch pushes live.
Changes or additions to these .yml files will automatically trigger a rebuild of the staging and production sites respectively.

# Other Tools

See [Tools Readme](tools/README.md).
