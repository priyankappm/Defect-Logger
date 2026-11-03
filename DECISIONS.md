# Decisions

## 1. Where the AI got it wrong
While planning the commit steps, the AI (Claude) told me the submission deadline was
"tomorrow" and called its own earlier "that is today, so don't wait" a mistake. That
correction was itself wrong: the deadline is Tuesday 3 November 2026, 6:00 PM IST, and
that day is today. The AI later retracted the retraction. Acting on the bad correction
would have cost me a day I did not have. I caught it because the date was re-checked
against the brief's own due date. The exchange is in the shared session (README link),
in the turn where the commit plan is given and the turn after it.
I did not find a bug in the generated code itself; the checks below are what I ran to
look for one.

Manual checks I ran against the CLI (all behaved as expected):
- `--sample-size 8.0.2` and `--sample-size kj`: clear "must be a whole number" error.
- `--sample-size 1000`: accepted (uses the 700 row, limits 14 and 30).
- `--severity minor1`: rejected with the list of valid severities.
- `--severity MINOR`: accepted and stored as `minor`.

## 2. What I chose not to build, and why
Everything listed as out of scope: no login, database, styling, deployment, multi-user
support, or editing/deleting defects. No web UI either: a CLI is allowed and the
interesting part is the verdict rule and its boundaries.

## 3. What was ambiguous
- A sample size that is not a whole number ("kj", "8.0.2", 2.5): treated as invalid, the
  same as a size below 1, with no verdict produced.
- No upper limit on sample size: 900 and 1000 both use the 700 row, as R1 says.
- Severity casing: accepted case-insensitively and stored lowercase.
- Blank defect description or blank batch ID: rejected.
- More defects than the sample size: not checked, because the brief does not say to.
- `start` on an existing state file overwrites it (one inspection per file).
- I checked the six required cases against R1-R3 and found no disagreement with the rules.

## 4. Three things that could still go wrong (not covered by tests)
- A description containing a newline is accepted and stored as-is, which would break the
  one-defect-per-line output of `list`.
- Two CLI runs at the same time could overwrite each other's writes to the JSON file.
- The limits table is hardcoded; a typo in a value would only be caught for the rows and
  boundaries my tests happen to check. A hand-edited state file is also only partly validated.
