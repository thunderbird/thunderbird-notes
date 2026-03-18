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
import re
import sys
from dataclasses import dataclass
from typing import Any, Iterable

import yaml


@dataclass(frozen=True)
class NotesRules:
    known_keys: frozenset[str]
    forbidden_keys: frozenset[str] = frozenset()
    validate_group: bool = False


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
        validate_group=True,
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


def _validate_android_beta_groups(
    path: str, data: dict, raw_text: str, notes: list
) -> list[str]:
    """Check that release versions, release.groups, and '# Beta N' comments are
    consistent for each beta N, and that notes under '# Beta N' use group: N."""
    errors = []
    release = data.get("release") or {}

    # Collect beta numbers (the N in bN) from release version strings ('18.0b2' -> 2)
    version_betas = {
        int(m.group(1))
        for r in (release.get("releases") or [])
        if isinstance(r, dict)
        for m in [re.search(r"b(\d+)$", str(r.get("version", "")))]
        if m
    }
    # Collect beta numbers from the groups list ('Fixed in beta 2' -> 2)
    # Beta 1 is omitted as its group entry is a blank space.
    group_betas = {
        int(m.group(1))
        for g in (release.get("groups") or [])
        if (m := re.search(r"beta\s+(\d+)", str(g)))
    }

    # Find '# Beta N' comments and record which beta section each note list item falls under.
    # note_beta maps note index -> beta number for notes that are under a Beta section.
    note_beta: dict[int, int] = {}
    in_notes = current_beta = None
    note_idx = 0
    for line in raw_text.splitlines():
        if line.startswith("notes:"):
            in_notes = True
        elif in_notes:
            if re.match(r"^\S", line) and not line.startswith("#"):
                break  # reached the next top-level key
            if m := re.match(r"\s*#+\s*Beta\s+(\d+)", line):
                current_beta = int(m.group(1))
            elif re.match(r"\s+-\s", line):  # start of a new note list item
                if current_beta is not None:
                    note_beta[note_idx] = current_beta
                note_idx += 1

    comment_betas = set(note_beta.values())

    # For each beta N seen across any of the three sources, check all required
    # sources contain it. Beta 1 skips the groups check since its entry is a space.
    for n in sorted(version_betas | group_betas | comment_betas):
        sources = [("release version", version_betas), ("'# Beta N' comment", comment_betas)]
        if n > 1:
            sources.append(("release.groups entry", group_betas))
        missing = [src for src, betas in sources if n not in betas]
        if missing:
            errors.append(f"{path}: beta {n} missing from: {', '.join(missing)}")

    # Verify each note's group value matches the beta section it appears under.
    for idx, beta in note_beta.items():
        if idx < len(notes) and isinstance(notes[idx], dict):
            group_val = notes[idx].get("group")
            if group_val != beta:
                errors.append(
                    f"{path}: notes[{idx}] is under '# Beta {beta}' "
                    f"but has group: {group_val!r}"
                )

    return errors


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

    # per-note key validation
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

    # android_beta group validation
    if rules.validate_group:
        with open(path, encoding="utf-8") as f:
            raw_text = f.read()
        errors.extend(_validate_android_beta_groups(path, data, raw_text, notes))

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
