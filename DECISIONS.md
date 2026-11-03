# Decisions

## 1. Where the AI got it wrong
<WRITE THIS YOURSELF from your real session: the specific bug or bad suggestion,
how you noticed, what you did, and the quoted exchange or where to find it.>

## 2. What I chose not to build, and why
Everything listed as out of scope: no login, database, styling, deployment, multi-user support,
or editing/deleting defects. Also no web UI: a CLI is allowed and the rule is the interesting part.

## 3. What was ambiguous
- Sample size that isn't a whole number ("abc", 2.5): treated as invalid, same as below 1.
- Severity casing: accepted case-insensitively and stored lowercase.
- Blank defect description: rejected.
- Empty batch ID: rejected.
- More defects than the sample size: not checked; the brief doesn't say to.
- `start` on an existing state file overwrites it (one inspection per file).
- I checked the six required cases against R1-R3 and found no disagreement.

## 4. Three things that could still go wrong (not covered by tests)
- The limits table is hardcoded; a typo in a value would only be caught by the boundary cases I wrote.
- Two CLI runs at the same time could overwrite each other's writes to the JSON file.
- A hand-edited or very old state file with unexpected fields is only partly validated.
