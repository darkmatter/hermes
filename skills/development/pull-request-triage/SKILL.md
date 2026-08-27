---
name: pull-request-triage
description: Code review and PR lifecycle — request reviews from subagents, triage open PRs, manage Graphite stacks, and merge. Use when reviewing work before merge, triaging PR queues, or managing stacked PRs.
---

# Code Review & PR Triage

Use this skill for the full PR lifecycle: requesting code reviews on completed
work, triaging open PRs, identifying merge-ready work, reviewing a PR queue,
or merging a GitHub/Graphite stack.

## Code Review Checklist

When reviewing a PR (directly or via subagent), use the checklist at
`references/code-review-checklist.md` — covers bugs, security, performance,
style, and tests, plus the standard output format (File:Line, Severity,
What's wrong, Fix) and verdict (APPROVE / REQUEST_CHANGES / COMMENT).

## Requesting Code Review (Pre-Merge)

Dispatch a code-reviewer subagent to catch issues before they cascade. The
reviewer gets precisely crafted context — never your session's history.

**Core principle:** Review early, review often.

### When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing a major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing a complex bug

### How to Request

1. **Get git SHAs:**
   ```bash
   BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
   HEAD_SHA=$(git rev-parse HEAD)
   ```

2. **Dispatch a code-reviewer subagent** via `delegate_task` with:
   - What was implemented
   - Plan or requirements
   - BASE_SHA and HEAD_SHA
   - Brief description

3. **Act on feedback:**
   - Fix Critical issues immediately
   - Fix Important issues before proceeding
   - Note Minor issues for later
   - Push back if reviewer is wrong (with reasoning)

### Red Flags

- Never skip review because "it's simple"
- Never ignore Critical issues
- Never proceed with unfixed Important issues
- Never argue with valid technical feedback without reasoning

## PR Triage & Merge

## Inventory

1. Start with a repo/status sanity check:
   - `git status --short --branch`
   - `gh pr list --state open --limit 50 --json number,title,author,updatedAt,createdAt,headRefName,baseRefName,isDraft,reviewDecision,mergeStateStatus,url`
2. For each PR that may need action, inspect details:
   - `gh pr view <number> --json number,title,author,isDraft,mergeStateStatus,reviewDecision,baseRefName,headRefName,updatedAt,url,statusCheckRollup,comments,reviews,mergeable`
3. Summarize in actionable buckets, not raw chronological order:
   - ready / almost ready to merge
   - needs review
   - needs author action or conflicts
   - failing checks
   - draft/WIP
   - stacked/downstack waiting

## Reading CI and review state

- `reviewDecision: APPROVED` plus all required checks successful usually means merge-ready.
- `mergeStateStatus: DIRTY` or `mergeable: CONFLICTING` means author action is needed before merge.
- `BLOCKED` can mean required review missing, changes requested, branch protection, or merge queue state. Inspect reviews and checks before deciding.
- `UNSTABLE` on stacked Graphite PRs often means a downstack PR is still open or Graphite mergeability is pending, not necessarily bad code.
- Do not call a PR merged until `gh pr view <number> --json mergedAt` returns a non-null timestamp.

## Graphite stacks

Identify stack order by matching `headRefName` of a downstack PR to `baseRefName` of the next PR. Merge from trunk upward.

Useful non-interactive commands:

```bash
gt get <top-pr-or-branch> --remote-upstack --force --no-interactive --checkout
gt merge --dry-run --no-interactive
gt merge --no-interactive
```

Typical Graphite output and interpretation:

- `Handed off to merge queue` — the bottom PR is queued; wait for it to land.
- `Waiting on downstack` — do not force the upstack PR; retry after lower PRs merge.
- `Waiting on CI` — inspect `statusCheckRollup`; Graphite may have an in-progress mergeability check even when GitHub checks look green.

## Merge workflow

1. Verify repo merge strategy if needed:
   - `gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,deleteBranchOnMerge --jq .`
2. Queue or merge the bottom PR first. If GitHub says the branch is managed by a merge queue or already queued, treat that as progress and verify with `gh pr view`.
3. For Graphite stacks, fetch the full stack with `gt get`, run `gt merge --dry-run`, then `gt merge` only when Graphite says the stack is ready.
4. If the queue wait is long, start a tracked background watcher with `notify_on_complete=true` that:
   - periodically checks each PR's `state` and `mergedAt`
   - refreshes the stack with `gt get <top> --remote-upstack --force --no-interactive --checkout`
   - retries `gt merge --no-interactive`
   - exits successfully only when every PR has `mergedAt` set
5. Report the watcher session id and current blocker. Do not say the stack merged until verified.

## Reporting format

Keep the summary terse and operational:

- What was queued/merged
- What remains blocked and why
- Exact PR numbers
- Any background watcher/session id
- Verification status from `gh pr view`

## Pitfalls

- `gh pr merge --auto --squash` can return success-like output while only handing the PR to a merge queue. Verify `mergedAt` afterward.
- Do not merge a top-of-stack PR before downstack PRs land.
- Do not mistake Graphite's in-progress mergeability check for a failed CI check.
- Use non-interactive flags; avoid commands that prompt during agent runs.
