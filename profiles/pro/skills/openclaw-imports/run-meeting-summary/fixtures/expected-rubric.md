# Manual Evaluation Rubric

The skill should pass these checks before meaningful changes are merged.

## Source Resolution

- Accepts pasted transcript or summary.
- Accepts explicit local paths and URLs.
- Accepts loose requests like "import my last meeting from Granola".
- Accepts participant-based requests like "import my last one-on-one with John Doe".
- Asks a short disambiguation question only when there are multiple plausible matches or no source can be found.

## Summary Quality

- Produces a concise work-focused summary.
- Extracts decisions, action items, owners, open questions, and relevant context.
- Keeps provider/source metadata safe and useful.
- Does not retain the raw artifact by default.

## Safety

- Removes personal, private, gossip-adjacent, and non-work material.
- Converts person-focused critique into neutral process language only when useful.
- Does not reveal removed sensitive details in the safety report.
- Stops and asks when the destination should be restricted instead of broad internal.

## Obsidian Behavior

- Uses the existing vault project structure.
- Uses `state: working` for new notes.
- Checks for duplicates before writing.
- Presents the review gate before saving.
- Writes only after explicit user approval.
