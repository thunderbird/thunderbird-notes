# Thunderbird Desktop Release Notes

## Scope

These instructions apply **only** to Thunderbird Desktop release notes in:

- `beta/`
- `release/`
- `esr/`

They do not apply to `android_beta/`, `android_release/`, `archive/`,
`mozilla_archive/`, or tooling in this repo. See `README.md` for the full YAML
format.

## Selecting notes

When asked to draft notes for Bugzilla bug numbers or links:

1. Look up the bugs on bugzilla.mozilla.org, reading the description, relevant
   comments, and landed patches to identify the actual user-facing change.
   Make as few Bugzilla requests as possible:
   - Fetch all bugs in a single public REST API request, limited to the
     fields you need, e.g.
     `https://bugzilla.mozilla.org/rest/bug?id=111,222,333&include_fields=id,summary,status,resolution,target_milestone,cf_status_thunderbird_<N>`
     Field names must be explicit (wildcards are silently ignored); replace
     `<N>` with the target version, e.g. `cf_status_thunderbird_161` or
     `cf_status_thunderbird_esr153`.
   - Fetch comments or attachments only for bugs whose user-facing change is
     still unclear after that request, and batch those too where possible.
   - Do not re-fetch a bug already retrieved in the current session unless
     its landing status needs rechecking.
   - Prefer the REST API over scraping bug pages in HTML.
2. Recommend notes for meaningful user-facing features, behavior changes, and
   fixes. Exclude internal refactoring, build changes, and test-only work unless
   they also change user-facing behavior.
3. Exclude changes confined to features that are not enabled on the target
   channel. Check preferences and build conditions rather than relying on bug
   titles.
   - `release/` and `esr/`: exclude features only enabled in Nightly or Beta.
   - `beta/`: exclude features only enabled in Nightly. Prefix notes for
     features enabled in Beta but not Release with `(Beta only) `, e.g.
     `(Beta only) Unread count badges are available on Linux taskbars`. The
     prefix counts toward the 80-character limit.
4. If a bug has multiple patches, document only the patches that landed in the
   target version. Patches that landed in earlier versions, or that have not
   yet reached the target version's branch, are out of scope for that note.
   Determine this from the changesets on the relevant repository (e.g.
   `comm-central` for the version's Nightly cycle, or uplifts to
   `comm-beta`, `comm-release`, or `comm-esr<N>`), not from the bug's
   overall status. If you cannot tell which patches landed where, say so.
5. Group minor visual and usability fixes under a general
   "Visual and UX improvements" note when appropriate.
6. Check current landing information. Cached bug status may be stale. A
   retrieval failure does not mean a bug is private or that its fix has not
   landed. Try the public Bugzilla REST API or repository changesets when
   needed. Clearly identify anything you cannot verify; never invent details.
7. When given bug descriptions, patches, or test plans, use that information to
   draft or refine the notes.

## Classifying notes

- `new`: A genuinely new user capability
- `changed`: An intentional change to existing behavior
- `fixed`: Correction of unintended or broken behavior

## Writing rules

- Each note must be 80 characters or fewer.
- Use present tense for `new` and `changed`.
- Use past tense for `fixed`, describing what was broken.
- Do not begin notes with "Adds" or "Fixed".
- Use concise, plain, user-facing language.
- Avoid implementation details and trailing periods.
- Accurately describe the landed patch, which may cover less than the original
  report.
- Wrap Thunderbird preference names in backticks, e.g.
  ``Chat settings tab remained visible when `mail.chat.enabled` was false``.
- If a note contains a quoted string, wrap the entire note in single quotes,
  e.g. `'The Subscribe dialog continued to show "Please wait" after loading'`.
  Escape any apostrophe inside single quotes by doubling it (`''`).
- Quote notes that contain other YAML-significant characters (`:`, leading
  `*`, leading `` ` ``, etc.).

## Output format

```yaml
  - note: <release-note>
    tag: new | changed | fixed
    bugs: [<bug-number>]
```

- Sort entries in this order: new, changed, fixed.
- Do not put blank lines between entries within a section.
- Combine related bugs when one note accurately covers them.
- For a single bug, return only its YAML entry unless clarification is
  necessary.
- For batches, briefly flag unresolved verification issues outside the YAML.

When editing a notes file directly, follow the existing layout: `# New`,
`# Changed`, and `# Fixed` comment headers, with a blank line between sections.

## Other tasks

When given lists or release-note files, also support comparing included bug
numbers, identifying missing bugs, removing specified bugs, and returning
comma-separated bug lists when requested.
