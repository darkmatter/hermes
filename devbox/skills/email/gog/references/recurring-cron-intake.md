# Recurring inbox-intake cron

Use this when creating, checking, or editing the scheduled Cooper inbox sweep. Intake only — card workers still own autonomous-versus-HITL.

## Status check

Do not assume the sweep exists.

1. `hermes cron list --all`
2. Read `~/.hermes/cron/jobs.json` on the default profile
3. Other profiles (`devbox`, `planner`, `worker`) may have empty cron dirs

A one-shot that merely pins `cooper-email-inbox-triage` is not the sweep. The sweep job is named **Email inbox triage**.

## Create or update (do not duplicate)

Prefer `cronjob(action='update')` on the existing sweep.

```
cronjob(
  action="create",
  name="Email inbox triage",
  schedule="every 6h",
  skills=["cooper-email-inbox-triage", "gog", "himitsu"],
  continuity=true,
  attach_to_session=true,
  prompt=<template below>
)
```

If the creating session has no live gateway channel, Hermes stores `deliver: local`. Labels and Kanban still update; the HITL batch will not appear in chat until `deliver` points at a connected platform.

## Prompt template

See `cooper-email-inbox-triage` for the intake contract. Cron prompts must be self-contained: both accounts, himitsu unlock, `--gmail-no-send`, 30 classify candidates/account, classify+enqueue, archive verified Waiting/Delegated/Done (100-thread drain/account), mandatory random full-thread audit (5/account; stratified 10/account for bulk), at most 3 HITL items, no send/delete/pay.
