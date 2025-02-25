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

REQUIREMENTS_IMPORT = {
    "102": "102.0",
    "115": "115.0",
    "128": "128.0esr",
    "beta": "116.0beta",
}

NO_AUTO_UPDATES = """**Thunderbird version 115 is only offered as direct download from
thunderbird.net and not as an upgrade from Thunderbird version 102 or
earlier. A future release will provide updates from earlier versions.**"""

TMPL_128_TEXT = """**For help and a quick start on Thunderbird 128, see
[Thunderbird 128 Nebula FAQ](https://support.mozilla.org/en-US/kb/thunderbird-128-nebula-faq)**

**For more on all the new features in Thunderbird 128, see
[What’s New in Thunderbird 128](https://www.thunderbird.net/thunderbird/128.0/whatsnew/).**

**System Requirements:** [Details](/en-US/thunderbird/128.0esr/system-requirements/)

- Windows: Windows 10 or later
- Mac: macOS 10.15 or later
- Linux: GTK+ 3.14 or higher
"""

TMPL_115_TEXT = """**For help and a quick start on Thunderbird 115, see
[Thunderbird 115 Supernova FAQ](https://support.mozilla.org/en-US/kb/thunderbird-115-supernova-faq).**

**For more on all the new features in Thunderbird 115, see
[What’s New in Thunderbird 115](https://www.thunderbird.net/thunderbird/115.0/whatsnew/).**

**System Requirements:** [Details](/en-US/thunderbird/115.0/system-requirements/)

- Windows: Windows 7 or later
- Mac: macOS 10.12 or later
- Linux: GTK+ 3.14 or higher
"""

TMPL_102_TEXT = """<p style="color: #d70022; font-weight: bold">Thunderbird 115 is now available! The "Supernova" UI features
provide an updated user interface and is designed to be more modern, customizable, and with code that is easier to
maintain and improve.</p>

**[Learn more about "Supernova"](https://blog.thunderbird.net/tag/supernova/)**

**System Requirements:** [Details](/en-US/thunderbird/102.0/system-requirements/)

- Windows: Windows 7 or later
- Mac: macOS 10.12 or later
- Linux: GTK+ 3.14 or higher
"""

TMPL_BETA_TEXT = """**These notes apply to Thunderbird version {ver_major} beta 1 released {human_date}.**

**System Requirements:** [Details](/en-US/thunderbird/{ver_major}.0beta/system-requirements/)

- Windows: Windows 10 or later
- Mac: macOS 10.15 or later
- Linux: GTK+ 3.14 or higher
"""

TMPL_RELEASE_TEXT = """**System Requirements:** [Details](/en-US/thunderbird/{ver_major}.0/system-requirements/)

- Windows: Windows 10 or later
- Mac: macOS 10.15 or later
- Linux: GTK+ 3.14 or higher
"""

TMPL_RELEASES_TEXT = {
    "102": TMPL_102_TEXT,
    "115": TMPL_115_TEXT,
    "128": TMPL_128_TEXT,
    "release": TMPL_RELEASE_TEXT,
    "beta": TMPL_BETA_TEXT,
}

TMPL_SEC_NOTE = "[Security fixes](https://www.mozilla.org/en-US/security/known-vulnerabilities/thunderbird/#{thunderbird_version})"
