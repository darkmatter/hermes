# Kanban incident recovery pattern

This is a compact, validated red-to-green pattern for future worker incidents. It is an example shape, not a permanent claim about any provider, model, host, or credential state.

## Symptom

A board appeared broadly broken because its history contained many technical failures. The live card columns alone were ambiguous:

- multiple historical runs had crashed;
- some current cards were `blocked`;
- two cards were `ready` but never selected by dispatch;
- successful domain-worker runs existed on the same board.

The initial failure count therefore mixed four different things: run attempts, affected tasks, historical errors, and valid HITL blocks.

## Evidence reduction

The investigation first grouped cards by deterministic workflow metadata and reduced each card to its latest run.

That exposed two separate populations:

1. Domain intake cards whose latest runs were either `completed` or intentionally `blocked`, all with `error=null`.
2. A much smaller set of older cards responsible for every technical crash and spawn failure.

This avoided searching hundreds of incidental `error` strings in domain content and old logs.

## Tight repro

The affected cards were visibly `ready`, but this command selected nothing:

```bash
hermes kanban --board <board> dispatch --dry-run --max 2 --json
```

That was the red loop. A normal healthy result needed to list the exact two cards under `spawned`.

## Root-cause tracing

The dispatcher-level error said the worker exited without a terminal Kanban call. Reading the worker log showed that this was only a wrapper symptom: an upstream model/provider initialization error occurred before the first tool call.

A later failed start left task/profile failure state that matched a respawn guard. The cards remained `ready`, but the guard suppressed dispatch.

Durable lesson:

> When a worker exits without `kanban_complete` or `kanban_block`, inspect the earliest worker-log failure before concluding the model ignored protocol.

## Recovery

The repair sequence was:

1. Identify a provider/model pair proven by a recent successful worker session.
2. Pin the affected tasks to that known-good pair.
3. Clear the stale task/profile failure state using supported Kanban assignment transitions rather than editing SQLite.
4. Re-run dry dispatch and require the exact cards under `spawned`.
5. Perform the real narrow dispatch.
6. Monitor heartbeats and runs until every retry ends through `kanban_complete` or `kanban_block`.

Template:

```bash
# Correct execution configuration first.
hermes kanban --board <board> set-model <task> <model> --provider <provider>

# On versions where the guard is scoped to task/profile and no dedicated
# reset verb exists, make an explicit recovery transition.
hermes kanban --board <board> assign <task> none
hermes kanban --board <board> assign <task> <known-good-profile>

# Red must become green before real dispatch.
hermes kanban --board <board> dispatch --dry-run --max <n> --json
hermes kanban --board <board> dispatch --max <n> --json
```

Always consult live `--help`; prefer a dedicated reset/retry command if the installed version provides one.

## Cascade verification

Both repaired cards reached `completed` with `error=null`. Completing one parent immediately promoted a dependent child, which the gateway auto-dispatched. The incident was not complete until that child also reached a valid terminal state.

The child ended `blocked` with `error=null` for a genuine approval/external-action reason. That was HITL, not a worker failure.

Final checks were:

```bash
hermes kanban --board <board> stats
hermes kanban --board <board> diagnostics --json
hermes kanban --board <board> list --json --sort created-desc
```

The completion proof required:

- diagnostics empty or every finding explained;
- no unexpected `ready` cards;
- no unexpected `running` cards;
- repaired latest runs had terminal outcomes and `error=null`;
- workflow-scoped cards were counted separately from unrelated board history;
- any newly promoted child was included in the report.

## Reusable lessons

1. **Count tasks and attempts separately.** Fourteen failed runs may belong to only two cards.
2. **Latest run defines live health.** Historical failures remain audit evidence, not current incident counts.
3. **Blocked is semantic, not technical.** Read `outcome`, `error`, summary, and policy.
4. **Wrapper errors can obscure the first failure.** Read the worker log from initialization forward.
5. **Ready does not imply spawnable.** Dry dispatch is the tight guard/recovery test.
6. **Prove the replacement path.** Use a model/profile from a recent successful worker, not one that merely appears configured.
7. **Fix before reset.** Clearing counters without repairing the cause creates a loop.
8. **Use supported transitions.** Preserve Kanban events and invariants; avoid direct production database edits.
9. **Watch cascades.** Parent completion can immediately create new running work.
10. **Separate technical and business reporting.** Technical failures should be retried after repair; genuine HITL should remain visible to the user.
