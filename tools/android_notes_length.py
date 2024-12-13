#!/usr/bin/env python3

import argparse
import os
import requests
import tempfile
import yaml
import sys

from jinja2 import Template


def check_notes_length(version, application, maxlen):
    """Check if the number of characters in short notes exceeds maxlen"""
    tb_notes_filename = f"{version}.yml"
    tb_notes_directory = "android_release"
    if "0b" in version:
        tb_notes_filename = f"{version[0:-1]}eta.yml"
        tb_notes_directory = "android_beta"

    notes_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        tb_notes_directory,
        tb_notes_filename,
    )

    with open(notes_path) as fp:
        yaml_content = yaml.safe_load(fp.read())

    releases_dict = yaml_content["release"]["releases"]
    if not any(version in releases.values() for releases in releases_dict):
        print(f"ERROR: Release {version} not found")
        sys.exit(1)

    total_len = 0
    with tempfile.TemporaryFile(mode="w+") as short_file:
        if application == "thunderbird":
            short_file.write(
                f"Thunderbird for Android version {version}, "
                "based on K-9 Mail. Changes include:\n"
            )
        for note in yaml_content["notes"]:
            if ("0b" not in version) or (
                "0b" in version and note["group"] == int(version[-1])
            ):
                if "note" in note:
                    if (
                        note.get("thunderbird_only", False) and application == "k9mail"
                    ) or (
                        note.get("k9mail_only", False) and application == "thunderbird"
                    ):
                        continue
                if "short_note" in note:
                    short_file.write(f"- {note["short_note"].strip()}\n")

        short_file.seek(0)
        content = short_file.read().rstrip()
        print(f"Short notes content:\n{content}")
        print(f"Short notes maximum length: {maxlen} characters")
        print(f"Short notes actual length: {len(content)} characters")
        if len(content) > maxlen:
            print("ERROR: Maximum notes length exceeded")
            sys.exit(1)
        else:
            print("SUCCESS: Maximum notes length not exceeded")
        print("")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str, help="Version name for this release")
    args = parser.parse_args()

    maxlen = 500
    for application in ["k9mail", "thunderbird"]:
        print(f"== {application} ==")
        check_notes_length(args.version, application, maxlen)


if __name__ == "__main__":
    main()
