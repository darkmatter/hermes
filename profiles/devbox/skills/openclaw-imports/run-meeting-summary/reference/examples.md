# Examples

## Loose Provider Request

User:

```text
import my last meeting from Granola
```

Expected behavior:

- Search Granola first.
- Pick the latest meeting if there is one clear match.
- If there are several recent meetings, show a short picker.
- Draft a company-safe summary and show the review gate.

## Participant Request

User:

```text
import my last one-on-one with John Doe
```

Expected behavior:

- Search available meeting sources and calendar metadata for John Doe.
- Prefer one-on-one meetings over group meetings.
- If there are multiple matches, ask the user to choose.
- Do not include personal or interpersonal details in the summary.

## Provider Alias

User:

```text
import my latest MeetJamie note
```

Expected behavior:

- Treat MeetJamie and Jamie as provider hints.
- Search available exports, docs, downloads, and connected sources.
- Ask for an export only if no available source can be found.

## Pasted Transcript

User pastes a transcript and asks for a company-safe summary.

Expected behavior:

- Treat the pasted text as the source.
- Normalize it into the standard note format.
- Do not write until the user approves the review gate.

## Review Gate

```markdown
Destination: Projects/darkmatter/nixmac/2026-05-12 cooper nixmac sync.md
Duplicate check: none found
Safety check: passed with removals

Removed categories:
- Personal life details
- Gossip-adjacent teammate commentary

Draft:
<full note>

Reply with:
- submit
- edit: <changes>
- discard
```
