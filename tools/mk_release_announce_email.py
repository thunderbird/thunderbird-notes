#!/usr/bin/python3

"""Generate an email to thunderbird-drivers and support
and open a Thunderbird compose window with content
and recipient fields filled in.

The release notes YAML needs to be written as the
rendered notes are attached to the email.

The uplifts need to be pushed, versions updated, and
.gecko_rev.yml pinned to the mozilla revision.

The version and pinning information is pulled from the tip of the
provided repo (version.txt and .gecko_rev.yml).

Example:
    ./tools/mk_release_announce_email.py comm-esr78

Defaults to using "1" for the build number in the subject line.

To change the build number:
    ./tools/mk_release_announce_email.py comm-esr78 2

- "thunderbird" must be in $PATH.

"""


import sys
import os
import re
import json
import subprocess
import shutil

from urllib.request import urlopen
from collections import namedtuple

import yaml
import markupsafe
import markdown

GECKO_REV_URL = "https://hg.mozilla.org/releases/{repo}/raw-file/tip/.gecko_rev.yml"
MERCURIAL_TAGS_URL = "https://hg.mozilla.org/releases/{repo}/json-tags"
CUR_VERSION_URL = (
    "https://hg.mozilla.org/releases/{repo}/raw-file/tip/mail/config/version.txt"
)
CUR_VERSION_DISPLAY_URL = (
    "https://hg.mozilla.org/releases/{repo}/raw-file/tip/mail/config/version_display.txt"
)

SOURCE_URL = "https://hg.mozilla.org/releases/{repo}/file/{hash}"

REV_MD_TMPL = "[{link_text}]({link_url})"

RELEASE_EMAIL_SUBJECT = "Thunderbird {release_version} - build {build}"
RELEASE_EMAIL_HTML = """**Thunderbird {release_version}** - build {build}

{repo}: {comm_link}
{moz_repo}: {moz_link}

"""

ReleaseRevs = namedtuple("ReleaseRevs", ["comm_rev", "gecko_ref", "gecko_rev"])


def get_revs(c_repo):
    with urlopen(GECKO_REV_URL.format(repo=c_repo)) as response:
        data = response.read()
        gecko_rev_data = yaml.safe_load(data)
        gecko_ref = gecko_rev_data["GECKO_HEAD_REF"]
        gecko_rev = gecko_rev_data["GECKO_HEAD_REV"]

    with urlopen(MERCURIAL_TAGS_URL.format(repo=c_repo)) as response:
        data = response.read()
        tags_data = json.loads(data)
        comm_rev = tags_data["node"]

    return ReleaseRevs(comm_rev=comm_rev, gecko_ref=gecko_ref, gecko_rev=gecko_rev)


def markdown_render(md_source):
    """Strips the outer <p> element from rendered markdown."""
    return re.sub(
        "(^<P>|</P>$)",
        "",
        markupsafe.Markup(markdown.markdown(md_source)),
        flags=re.IGNORECASE,
    )


def gen_preview(version):
    subprocess.run("python preview.py {} email".format(version), shell=True, check=True)


def main(comm_repo, build):
    moz_repo = comm_repo.replace("comm", "mozilla")

    with urlopen(CUR_VERSION_URL.format(repo=comm_repo)) as response:
        data = response.read()
        release_version = data.strip().decode("utf-8")
    with urlopen(CUR_VERSION_DISPLAY_URL.format(repo=comm_repo)) as response:
        data = response.read()
        release_display_version = data.strip().decode("utf-8")

    revs = get_revs(comm_repo)

    comm_source_url = SOURCE_URL.format(repo=comm_repo, hash=revs.comm_rev)
    comm_source_text = revs.comm_rev[:12]
    comm_link = REV_MD_TMPL.format(link_text=comm_source_text, link_url=comm_source_url)

    moz_source_url = SOURCE_URL.format(repo=moz_repo, hash=revs.gecko_rev)
    moz_source_text = "{g_ref}/{g_rev}".format(
        g_ref=revs.gecko_ref, g_rev=revs.gecko_rev[:12]
    )
    moz_link = REV_MD_TMPL.format(link_text=moz_source_text, link_url=moz_source_url)

    notes_suffix = ""
    if (comm_repo == 'comm-beta'):
        notes_suffix = 'beta'
    notes_version = "{}{}".format(release_version,notes_suffix)

    email_subject = RELEASE_EMAIL_SUBJECT.format(
        release_version=release_display_version, build=build
    )
    email_body_html = markdown_render(
        RELEASE_EMAIL_HTML.format(
            release_version=release_display_version,
            build=build,
            repo=comm_repo,
            moz_repo=moz_repo,
            comm_link=comm_link,
            moz_link=moz_link,
        )
    )
    gen_preview(notes_version)
    attach_fn = "Thunderbird_{}.html".format(release_display_version.replace(".", "_"))
    shutil.move("preview.html", attach_fn)

    cc = "Thunderbird Support <support-crew@discuss.thunderbird.net>"
    if comm_repo == "comm-beta":
        cc += ";TB Beta <beta@discuss.thunderbird.net>"
    subprocess.run("thunderbird -compose 'format=html','attachment={}','to={}','cc={}','subject={}','body={}'"
                   .format(os.path.abspath(attach_fn),
                           "Thunderbird Drivers <thunderbird-drivers@mozilla.org>",
                           cc,
                           email_subject, email_body_html), shell=True)


def do_builderr(build_str):
    print("Invalid build number: {}".format(build_str))
    sys.exit(3)


if __name__ == "__main__":
    if not sys.argv[1]:
        print("Provide a repository name: comm-beta/comm-esr78/comm-esr91")
        sys.exit(1)
    if sys.argv[1] not in ("comm-beta", "comm-esr78", "comm-esr91"):
        print("Invalid repository: {}".format(sys.argv[1]))
        sys.exit(2)

    if len(sys.argv) < 3:
        print("Defaulting to build one")
        sys.argv.append("1")
    else:
        try:
            bi = int(sys.argv[2])
        except ValueError:
            do_builderr(sys.argv[2])
        if bi > 5:
            # arbitrary limit for giggles
            do_builderr(sys.argv[2])

    main(*sys.argv[1:])
