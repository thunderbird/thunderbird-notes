# Thunderbird Release Notes

## Scope

These instructions apply **only** to release notes in:

- Thunderbird Desktop: `beta/`, `release/`, `esr/`
- Thunderbird for Android: `android_beta/`, `android_release/`

They do not apply to `archive/`, `mozilla_archive/`, or tooling in this repo.
See `README.md` for the full YAML format.

Sections up to and including "Other tasks" describe Desktop notes. The
"Classifying notes" and "Writing rules" sections also apply to Android. See
"Thunderbird for Android" at the end for Android-specific rules, which take
precedence for `android_beta/` and `android_release/`.

## Where notes come from

- `beta/`: Draft notes from scratch using the process below.
- `release/` and `esr/`: Do not draft new notes. Carry the notes forward from
  the `beta/` files where the change first shipped, whether it reached the
  target branch by a merge or an uplift. Reuse the beta wording, tag, and bug
  numbers as they are.
  - Drop entries for features that are not enabled on the target channel
    (see rule 3 below). Remove the `(Beta only) ` prefix only if the feature
    is now enabled on the target channel; otherwise drop the entry.
  - If a bug has no note in any beta file, flag it rather than writing one.

## Finding bugs for a beta

When no bug list is given, a bug belongs to beta version `<N>` if either:

- its Target Milestone is `<N> Branch`, or
- its `cf_status_thunderbird_<N>` tracking flag is `fixed` (or `verified`),

and its `cf_status_thunderbird_<N-1>` flag is not `fixed` or `verified`.

Never add a note for a bug whose `cf_status_thunderbird_<N-1>` flag is
`fixed` or `verified`, even if its Target Milestone is `<N> Branch` or its
`<N>` flag is `fixed`. It was uplifted to and shipped in the previous version,
so its note belongs there.

Restrict the search to the Thunderbird products: `Calendar`, `Chat Core`,
`MailNews Core`, and `Thunderbird`. Firefox uses the same milestone names.
Do not filter on resolution: bugs left open after a partial landing can still
qualify. Example for 162:

`https://bugzilla.mozilla.org/rest/bug?product=Thunderbird&product=MailNews%20Core&product=Calendar&product=Chat%20Core&f1=OP&j1=OR&f2=target_milestone&o2=equals&v2=162%20Branch&f3=cf_status_thunderbird_162&o3=anywords&v3=fixed%20verified&f4=CP&f5=cf_status_thunderbird_161&o5=nowords&v5=fixed%20verified&include_fields=id,product,component,summary,type,keywords,resolution,target_milestone,cf_status_thunderbird_161,cf_status_thunderbird_162&limit=0`

## Selecting notes

When asked to draft notes for Bugzilla bug numbers or links (`beta/` only; see
above for `release/` and `esr/`):

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

## Thunderbird for Android

### Where notes come from

- `android_beta/`: Draft notes from scratch using the process below.
- `android_release/`: Do not draft new notes. Carry the notes forward from the
  matching `android_beta/` file, reusing the wording, tag, pull requests, and
  issues as they are. Release files do not use the `group` field.
  - Drop entries for features that are not enabled on the release channel.
    Use the `(Beta only) ` prefix the same way as Desktop: remove it only if
    the feature is now enabled on release; otherwise drop the entry.
  - If a pull request has no note in the beta file, flag it rather than
    writing one.
- There is no ESR for Android.

### Finding pull requests for a beta

Changes are tracked with milestones on
https://github.com/thunderbird/thunderbird-android/milestones. There are
always three open milestones named `Thunderbird <N>`:

- Largest number: Daily (`main` branch)
- Middle number: Beta (beta branch)
- Smallest number: Release (release branch)

For example, with "Thunderbird 25", "Thunderbird 26", and "Thunderbird 27",
25 is Release, 26 is Beta, and 27 is Daily.

To find changes for beta `<N>`, use the closed pull requests in the
`Thunderbird <N>` milestone. Do not add a note for a change that was also
fixed in the `Thunderbird <N-1>` milestone; it already shipped in the
previous version.

Make as few GitHub requests as possible, using the public REST API rather than
scraping HTML:

- Milestone titles differ from milestone numbers. Resolve them with
  `https://api.github.com/repos/thunderbird/thunderbird-android/milestones?state=open`.
- List the milestone's closed items in one request, e.g.
  `https://api.github.com/repos/thunderbird/thunderbird-android/issues?milestone=<milestone-number>&state=closed&per_page=100`.
  This returns both pull requests (items with a `pull_request` key) and
  issues. Follow pagination if there are more than 100.
- Fetch individual pull requests or issues only when the user-facing change is
  still unclear, and do not re-fetch items already retrieved in the session.

### Selecting notes

- Pull request labels override the selection rules below:
  - Always include a pull request labeled `report: include`, even if it would
    otherwise be excluded (e.g. internal, build, or test-only work).
  - Always exclude a pull request labeled `report: exclude`, even if it looks
    user-facing.
  - Labels are returned in the `labels` field of the milestone listing, so no
    extra requests are needed to check them.
- Consult both the pull request and the issue it fixes (e.g. "Fixes #11654" in
  the PR description) to determine the user-facing change. Describe what the
  merged pull request actually does.
- Recommend notes for meaningful user-facing features, behavior changes, and
  fixes. Exclude internal refactoring, build, CI, dependency, and test-only
  changes unless they also change user-facing behavior.
- Exclude changes confined to features that are not enabled on the target
  channel. In `android_beta/`, prefix notes for features enabled in Beta but
  not Release with `(Beta only) `.
- Do not group fixes under "Visual and UX improvements"; there are usually too
  few Android fixes to need it.
- Clearly identify anything you cannot verify; never invent details.

### Writing rules

- Follow the shared "Writing rules" above.
- `note` and `short_note` must each be 80 characters or fewer.
- `short_note` is usually identical to `note`. Shorten it only when needed to
  meet the total limit.
- The `short_note` values for a release can total no more than 500
  characters, checked separately for each app (K-9 Mail and Thunderbird).
  Verify with `python3 tools/android_notes_length.py <version>`, which also
  counts list markers and the Thunderbird header line.
- If shortening is not enough to meet the limit, omit `short_note` from the
  least significant notes (typically minor fixes) until it fits. Those notes
  still appear in the full release notes.
- Set `thunderbird_only: true` or `k9mail_only: true` if a change applies to
  only one app. Omit both when it applies to both.

### Output format

```yaml
  - note: <release-note>
    short_note: <short-release-note>
    pull_requests: [<pr-number>]
    issues: [<issue-number>]
    thunderbird_only: true
    tag: new | changed | fixed
    group: <beta-number>
```

- `short_note` (see above), `thunderbird_only`, and `k9mail_only` are
  optional. `group` is only used in `android_beta/` and is the beta number the
  change first shipped in.
- Sort entries new, changed, fixed within each group, following the existing
  `# Beta <n>`, `# New`, `# Changed`, and `# Fixed` comment headers.
- Within each section, sort entries by importance to users, most significant
  first. When dropping `short_note` values, start from the end of each section.
- Combine related pull requests and issues when one note accurately covers
  them.
