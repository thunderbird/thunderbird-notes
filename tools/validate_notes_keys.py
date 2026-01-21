#!/usr/bin/env python3
"""Validate allowed keys inside the top-level `notes:` list for notes directories.

Rules per directory:
- android_beta and android_release:
    allowed note keys are {note, short_note, pull_requests, issues, tag, group}
    and `group` must not appear in android_release.
- beta, esr, release:
    allowed note keys are {note, tag, bugs, group} and `group` must not appear
    in esr or release.
"""

import argparse
import glob
import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable

import yaml


@dataclass(frozen=True)
class NotesRules:
    known_keys: frozenset[str]
    forbidden_keys: frozenset[str] = frozenset()


RULES_BY_DIR: dict[str, NotesRules] = {
    "android_beta": NotesRules(
        known_keys=frozenset(
            {
                "note",
                "short_note",
                "pull_requests",
                "issues",
                "tag",
                "group",
                "thunderbird_only",
                "k9mail_only",
            }
        ),
        forbidden_keys=frozenset(),
    ),
    "android_release": NotesRules(
        known_keys=frozenset(
            {
                "note",
                "short_note",
                "pull_requests",
                "issues",
                "tag",
                "group",
                "thunderbird_only",
                "k9mail_only",
            }
        ),
        forbidden_keys=frozenset({"group"}),
    ),
    "beta": NotesRules(
        known_keys=frozenset({"note", "tag", "bugs", "group"}),
        forbidden_keys=frozenset(),
    ),
    "esr": NotesRules(
        known_keys=frozenset({"note", "tag", "bugs", "group"}),
        forbidden_keys=frozenset({"group"}),
    ),
    "release": NotesRules(
        known_keys=frozenset({"note", "tag", "bugs", "group"}),
        forbidden_keys=frozenset({"group"}),
    ),
}


def _iter_yaml_files(repo_root: str, directory: str) -> Iterable[str]:
    pattern = os.path.join(repo_root, directory, "*.yml")
    for path in sorted(glob.glob(pattern)):
        if os.path.isfile(path):
            yield path


def _load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _validate_notes_file(path: str, rules: NotesRules) -> list[str]:
    errors: list[str] = []

    try:
        data = _load_yaml(path)
    except Exception as e:
        return [f"{path}: failed to parse YAML: {e}"]

    if not isinstance(data, dict):
        return [f"{path}: expected top-level YAML mapping, got {type(data).__name__}"]

    notes = data.get("notes")
    if notes is None:
        return [f"{path}: missing top-level 'notes' key"]

    if not isinstance(notes, list):
        return [
            f"{path}: expected top-level 'notes' to be a list, got {type(notes).__name__}"
        ]

    for idx, note_entry in enumerate(notes):
        if not isinstance(note_entry, dict):
            errors.append(
                f"{path}: notes[{idx}] expected mapping, got {type(note_entry).__name__}"
            )
            continue

        keys = set(note_entry.keys())

        unknown_keys = keys - set(rules.known_keys)
        if unknown_keys:
            errors.append(
                f"{path}: notes[{idx}] has invalid keys {sorted(unknown_keys)}; "
                f"allowed keys are {sorted(rules.known_keys)}"
            )

        forbidden_present = keys & set(rules.forbidden_keys)
        if forbidden_present:
            errors.append(
                f"{path}: notes[{idx}] has forbidden keys {sorted(forbidden_present)}"
            )

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate allowed keys inside `notes:` entries for notes directories."
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to repo root (default: auto-detect from this script location).",
    )
    parser.add_argument(
        "--dirs",
        nargs="*",
        default=list(RULES_BY_DIR.keys()),
        help=f"Directories to validate (default: {', '.join(RULES_BY_DIR.keys())}).",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    all_errors: list[str] = []
    validated_files = 0

    for directory in args.dirs:
        rules = RULES_BY_DIR.get(directory)
        if rules is None:
            all_errors.append(
                f"Unknown directory '{directory}'. Known: {sorted(RULES_BY_DIR.keys())}"
            )
            continue

        for path in _iter_yaml_files(repo_root, directory):
            all_errors.extend(_validate_notes_file(path, rules))
            validated_files += 1

    if validated_files == 0:
        all_errors.append(
            "No YAML files found to validate. Check --repo-root and directory names."
        )

    if all_errors:
        for line in all_errors:
            print(line)
        return 1

    print(f"OK: validated {validated_files} YAML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
