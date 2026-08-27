# Reviewer output schema

The reviewer is constrained to produce output in this shape. Hook scripts and downstream parsers can rely on it.

## Line 1 — verdict

Exactly one of:

```
LGTM
LGTM with notes
BLOCK — <short reason, ≤80 chars>
```

## Body — issues list

Numbered list, each item:

```
N. <file:line if applicable> — <one-sentence problem>
   Why: <one-sentence failure mode>
   Fix: <optional one-line suggestion>
```

If `LGTM` with no notes, the body is empty (or absent).

## Optional trailing section

```
If I were doing this:
<≤3 sentence alternative approach>
```

Only present when the reviewer has a genuinely different angle worth surfacing.

## Parsing notes

- The verdict line is always the first non-empty line of stdout.
- Issues are zero-or-more, separated by blank lines.
- The `Why:` and `Fix:` sub-lines may be absent; only the top sentence is guaranteed.
- Trailing section, if present, starts with the literal string `If I were doing this:`.
