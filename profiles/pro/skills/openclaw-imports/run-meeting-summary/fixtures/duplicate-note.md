# Existing Note Duplicate Fixture

```markdown
---
type: meeting
origin: meeting-summary
state: working
people:
  - Farhan
  - Cooper
tags:
  - meetings
created: 2026-05-12
updated: 2026-05-12
meeting_date: 2026-05-12
---

# 2026-05-12 Cooper Nixmac Sync

## Summary

Cooper and Farhan aligned on the next nixmac narrative update: short-term goals, current state, StackPanel positioning, crypto work, engineering philosophy, current events, and Dark Matter vision.

## Source

- Provider: Granola
- Source reference: granola:meeting_abc123
- Source fingerprint: sha256:exampleduplicatehash
- Raw artifact retained: no
```

Expected duplicate signals:

- Same meeting date.
- Same title or participant set.
- Same provider ID or source fingerprint.
- Similar summary heading.
