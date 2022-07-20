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
                       "beta": "97.0beta",
                       }

TMPL_RELEASE_TEXT = """**Thunderbird version 102.0.2 is only offered as direct download from
    thunderbird.net and not as an upgrade from Thunderbird version 91 or
    earlier. A future release will provide updates from earlier versions.**

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
