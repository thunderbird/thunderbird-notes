"""
These are the templates used for the notes files.
"""

TMPL_HEADER = """---
release:
  release_date: XXXX-XX-XX
  text: |
    TEXT_TO_REPLACE

  import_system_requirements: XX.X

notes:
"""

REQUIREMENTS_IMPORT = {"release": "102.0",
                       "beta": "116.0beta",
                       }

TMPL_RELEASE_TEXT = """**For more on all the new features in Thunderbird 102, see
[What’s New in Thunderbird 102](https://www.thunderbird.net/thunderbird/102.0/whatsnew/).**

**System Requirements:** [Details](/en-US/thunderbird/102.0/system-requirements/)

- Windows: Windows 7 or later
- Mac: macOS 10.12 or later
- Linux: GTK+ 3.14 or higher
"""

TMPL_BETA_TEXT = """**These notes apply to Thunderbird version {ver_major} beta 1 released {human_date}.**

**System Requirements:** [Details](/en-US/thunderbird/{ver_major}.0beta/system-requirements/)

- Windows: Windows 7 or later
- Mac: macOS 10.12 or later
- Linux: GTK+ 3.14 or higher
"""
