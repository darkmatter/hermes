# Non-feature / non-bug asks from the OMP Hindsight bank

Mined 2026-08-17 from Hindsight Cloud bank `omp` (1,025 documents, 23,201 facts). Honcho stays the Hermes memory provider; this is a one-shot read.

Filter: user asked a coding agent to do something **other than ship a feature or fix a bug**. Feature-shaped “user requested X” memories (new DeepSeek config, print-mode docs, benchmarks) are excluded. Standing conventions that *are* maintainability rules are included even when they arrived as process, not a one-off prompt.

Sources: `user-preferences` mental model, `project-conventions-*`, keyword list (`cleanup` 198, `refactor` 184, `simplify` 73, `unused` 72, `prune` 119, `AGENTS.md` 48, `hygiene` 19, `leftover` 26, `dead code` 8, `surgical` 15), plus targeted recall.

---

## 1. Delete unused / dead / leftover — don’t recreate it

| When | Project | What was asked | Why it isn’t a feature |
|---|---|---|---|
| 2026-08-16 | agents | Zip archive has ~50 unused UI files; `SessionConsole` only needs a few primitives. | Inventory + delete unused surface. |
| 2026-08-16 | agents | Command-catalogue cleanup: remove broken `install` / `generate:agent`, prefix remaining with `dev:`, group into `develop`/`dev`/`test`/`smoke`/`secrets`. | Audit + reorganize the menu, not a new command. |
| 2026-08-16 | agents | Audit, repair, and reorganize the Prelude `x` command menu. | Explicit audit/reorg request. |
| 2026-08-10 | gitops | Remove unused raven-era PVC declarations from `manifests/base-node/pvc.yaml` + README. **Do not Sync** the Argo app — Sync would recreate dead claims. | Delete stale git declarations so cluster and git match. |
| 2026-08-09 | prelude | Clean duplicate Starship sections and an unused `project` segment left by failed prior edits. | Dedup leftover from a bad edit. |
| 2026-08-09 | gitops | Wipe `/tmp/litellm-smoke` and `/tmp/op-*.json` after SOPS/OP probes. | Secret-artifact hygiene. |
| 2026-08-08 | prelude | Net **−270 lines across 7 files** “to trim the diff and remove unnecessary code or tangents.” Also pull misplaced tests/sources out of the prompt commit. | Diff-diet. Not a feature. |
| 2026-08-08 | prelude | Remove unused `bce_stream` after simplifying `run_motd`. | Dead variable after a simplify. |
| 2026-08-06 | agents-flue | `@czxtm/configs` has **zero source consumers** — fails the deletion test. | Package-level unused. |
| 2026-07-31 | blog | Cleanup phase: temp files, worktrees (`alchemy-dm3`, `blog-og-deploy`), stale tags, merged `feat/og-images`. | Post-recovery workspace hygiene. |
| 2026-07-23 | web | Keep only Lora/Montserrat/Nunito; prune preview fonts + unused deps (`date-fns`, `recharts`, `jose`, …). | Dependency diet. User decided. |
| 2026-07-21 | prelude | Remove `KindHelp`, `help.go`, menu help, `modeHelp`; collapse manual package to docs-only. | Delete unused help paths for downstream simplicity. |
| 2026-07-21 | prelude | Remove FIGlet hero pipeline (`figlet`, `heroFile`, `NavNode.Hero`). | Drop unused docs-build machinery. |
| 2026-07-19 | centaur | Prefer a **clean cutover** over reserved knobs: delete unused `max_exec_output_bytes` / `OutputTooLarge` classifier rather than keep “for later.” | Don’t leave reserved dead API. |
| 2026-07-19 | centaur | Remove unused `_client/_server` duplexer, `stubThread`, `numberEnv`, leftover `goto`. | Post-refactor residue. |
| 2026-07-11 | gitops | Delete unused Slack scopes (`im:history`, `im:read`, …) after dropping those event subscriptions. | Least privilege, not a feature. |
| 2026-07-07 | gitops | Delete unused `alchemy.run.ts` / `src/backend.ts` / `src/env.ts` — broken by type drift, **no importers**. | Dead files. |
| 2026-07-03 | nixmac | Delete orphaned `BYOK_PROVIDERS` / `CLI_PROVIDERS` instead of resurrecting the removed type. | Dead after centralization. Don’t revive. |
| 2026-07-03 | platform | Delete unused menu scaffolding / `cn` imports to satisfy lint. | Hygiene to unblock the gate. |

**Standing rule implied:** if it has no importers and isn’t a public contract, delete it. Do not Sync/recreate dead resources. Do not keep “reserved for later” knobs.

---

## 2. Prefer the simpler existing thing — kill custom machinery

| When | Project | What was asked | Pattern |
|---|---|---|---|
| 2026-08-08 | prelude | Deprecate the command-output adapter + PTY harness in favor of **native bash-preexec**. Drops private FDs, lifecycle hooks, cleanup paths. | Replace a custom stack with the library’s hook. |
| 2026-08-08 | prelude | Isolated PREEXEC gated only on `_PRELUDE_WINDOW_BACKGROUND_SET=1` — drop MOTD ownership + command whitelist. | Fewer predicates. |
| 2026-08-08 | prelude | MOTD fringe: gradient `░▒▓` → uniform `░`. “Prefer uniform, minimalist visual effects. Reject gradient-based styling.” | Visual + code simplify. |
| 2026-08-08 | prelude | Prompt: drop decorative `╰─` row; single-row Starship layout. | Less chrome, fewer render bugs. |
| 2026-07-22 | centaur | Collapse sandbox pipe / OMP process / owner / keepalive into one `SessionHost`. **Remove 4,500–6,000 lines** from `centaur-session-runtime`. | One owner, delete the registry. |
| 2026-07-22 | centaur | Bounded OMP design: stay inside existing DB / session runtime / harness / wire protocol. `apiRs.replicaCount` stays 1. **No new services.** | Fence complexity; don’t add a plane. |
| 2026-07-22 | centaur | Writable `omp join` talks to `CollabHost` directly — delete guest-input bridge, dedup schema, per-participant policy. | Bypass instead of abstract. |
| 2026-07-21 | centaur | Clean-slate branch `feat/omp-export-stats-minimal` from `96f7071d` **replacing an overcomplicated implementation**. | Rewrite smaller, don’t patch the mess. |
| 2026-07-13 | prelude | User unhappy that `gum` is still in the shell script; wants it gone and the script more maintainable. | Delete the extra tool. |
| 2026-07-13 | skills | Remove dangling `writing-plans` handoff; approved design → implementation. Remove 1% activation + auto pre-plan brainstorming from `using-superpowers`. | Stop planning loops. |
| 2026-07-04 | gitops | **Prefer native library conventions over custom abstractions; keep customizations thin.** | Recurring preference. |
| 2026-06-28 | nixmac-web | Custom Polar integration should be `@polar-sh/tanstack-start` instead. | Use the vendor library. |
| 2026-06-28 | nixmac | Don’t add a `didCompleteOnboarding` flag — use a heuristic. Flags create bugs and block recovery. | Fewer bits of state. |
| 2026-06-30 | nixmac | Kill `ManualEvolve` / `ManualCommit`; auto-mint evolution IDs. Collapse duplicate React screens. | One path, delete the twin. |

**Standing rule implied:** if the library already does it, use that. If two paths exist, delete one. If a flag can be a heuristic, don’t add the flag.

---

## 3. Surgical diffs — no tangents, no unauthorized extras

| When | Project | What was asked | Pattern |
|---|---|---|---|
| 2026-08-08 | prelude | Trim the prompt commit: remove files that “did not belong.” | Commit contains only the ask. |
| 2026-07-23 | web | Discard **27 unauthorized uncommitted files** after the assistant wandered. | User said stop / revert extras. |
| 2026-07-29 | blog | “Stop all coding and deployment activities.” | Hard stop. Honor it. |
| 2026-07-31 | gitops | Do **not** modify production `auto` and `flash` models. | Explicit out-of-scope lock. |
| 2026-07-11 | gitops | Commit the sync workflow **separately** from other pending changes. | One concern per commit. |
| 2026-07-11 | gitops | SOPS `set` instead of full decrypt/re-encrypt — 61-line ciphertext churn → surgical key+MAC. | Minimize review noise. |
| 2026-06-29 | nixmac | Revert unrelated snapshot drift; keep only the 28 className flips. User checked the change was surgical, not the cause of flake. | Don’t launder pre-existing noise into the PR. |
| 2026-07-03 | nixmac | Commit-hygiene recipe for a dirty worktree: backup diffs → revert unrelated hunks → verify → commit → re-apply WIP. | Subset commits. Never `git add -A`. |
| standing | * | “PRs must be landed as narrow, focused fixes.” Human review required; CI is not enough. Self-approval prohibited. | Process. |
| standing | * | Never `git add -A docs`. Stage specific paths. | Hygiene. |
| 2026-08-10 | gitops | Assistant treated “cleanup approved” as “commit to main.” User later approved, but the misread is the lesson. | Cleanup approval ≠ land-on-main. |

**Standing rule implied:** the diff is the product. If it isn’t the ask, revert it. If the user says stop, stop.

---

## 4. Reorganize / rename / consolidate for cohesion

| When | Project | What was asked | Pattern |
|---|---|---|---|
| 2026-08-04 | agents-flue | Rename `workflow-contracts` → `utils`, `flue-model-providers` → `models`. “User prefers short simple package names” (`@czxtm/utils`). | Names that say what they are. |
| 2026-08-06 | agents-flue | Consolidate `ci-fixer/.../poll.ts` and `improvement-scout/.../weekly.ts` into `@czxtm/utils` — they duplicated a lifecycle and **had drifted**. | One scheduler; stop twin copies. |
| 2026-07-31 | blog | Consolidate shared code into one `darkmatter/sdk`; move `alchemy` in as an entrypoint. “Maintain only one shared SDK.” | Fewer repos, less choreography. |
| 2026-07-31 / 07-29 | blog | Prefer **self-contained packages** over root-level docs/tests/src split. User called the split “fragmented and lacking cohesion.” | Package = unit of cohesion. |
| 2026-07-22 | gitops | Immediate implementation of the **disentangling plan** so repo names match upstream. | Naming alignment. |
| 2026-07-11 | gitops | End state = exactly two repos (`centaur` + `centaur-overlay`). Delete `centaur-acme` only with explicit approval. | Consolidate, but deletion is gated. |
| 2026-07-11 | gitops | No perpetual feature branch; squash Darkmatter delta onto `main`. | Branch hygiene. |
| 2026-07-13 | skills | Keep `test-driven-development` as the canonical TDD skill; fold `tdd` into it; remove dangling transitions. | One skill per concern. |
| standing | * | Go: `src/cmd/` entrypoints, `src/internal/` core. Stateless, deterministic, allocation-light. | Layout for maintainability. |
| standing | * | `x` is the canonical surface; `menu` is a legacy PATH wrapper — **do not advertise it**. Update docs from `menu` → `x`. | One name in public. |

**Standing rule implied:** one owner, one name, one package. Twins drift. Short names beat clever names.

---

## 5. Docs, comments, AGENTS.md, skills — keep the contract true

| When | Project | What was asked | Pattern |
|---|---|---|---|
| 2026-07-13 | prelude | “Better code comments” on non-obvious contracts/invariants in `invocation.go`. | Comment the *why*, not the line. |
| standing | * | Documentation focuses on **why**: design intent, invariants, edge-case rationale. Sync via `docs-sync` / `docs-record`. | Docs are for the next agent. |
| 2026-07-10 | gitops | `centaur-drive.ts` docs were **stale** (claimed sandboxes hold no GitHub creds; Worker posts reviews). Update or delete. | Stale docs are a bug in the contract. |
| 2026-08-04 | agents-flue | AGENTS.md pinned a phantom “Flue 5”; lockfile is `@flue/*@2.0.1`. Correct the contract. | Don’t invent versions in agent docs. |
| 2026-07-23 | web | Assistant treated AGENTS.md **advisory blockers as user instructions**, then committed, pushed, and spawned 12 unsolicited subagents. | User prompt outranks advisory AGENTS.md. |
| 2026-07-22 | centaur | Remove local commit-approval rule from AGENTS.md. Local validated commits OK; **remote** mutations still need explicit authority. | Tighten the real gate; drop theater. |
| 2026-07-18 | gitops | Document existing attack vectors with example scenarios. | Security awareness doc, not a control. |
| 2026-07-11 | gitops | Handoff file in `~/Documents`. | Write the transfer, don’t just finish the task. |
| 2026-07-11 | gitops | Weekly workflow: recommend improvements via **new tools, integrations, or skills** for centaur-overlay. | Maintenance as a recurring scout, not a feature factory. |
| 2026-07-13 | skills | Specific trigger matching; monotonic Discovery → Design → Planning → Implementation → Verification; **no re-planning**; brainstorming off for mechanical refactors / approved plans. | Process hygiene in the skill corpus itself. |
| standing | * | Design-first: ADR/specs in `docs/superpowers/specs/` before implementation. Re-planning an approved design is forbidden. | Design is a maintainability artifact. |

**Standing rule implied:** AGENTS.md / comments / specs are load-bearing. Keep them true. Don’t let them override a live user instruction. Don’t add planning steps the user already killed.

---

## 6. How the user wants agents to work (process, not product)

These are standing asks to *agents*, not product features.

| When | Project | Ask |
|---|---|---|
| 2026-08-04 | prelude / agents-flue | Use **subagents** for the work; the parent only **reviews**. Planner/router delegates; only fixes when reviewing. |
| 2026-07-21 | centaur-overlay | Prefer `ctx.call_tool` over proxy-style invocation — easier to **grep, type-adapt, and fake**. |
| standing | * | TDD: red-green-refactor, observable behavioral tests, **no implementation-detail tests**. Approval only when public interfaces actually diverge. |
| standing | * | Fail-closed. Explicit error termination. Secret scanners fail on match or error. |
| standing | * | Inline single-expression functions unless they are durable contracts (3+ call sites, domain concept, or type guard). |
| standing | * | Dynamic `import()` only for runtime-selected specifiers, and only with an explanatory comment. |
| 2026-07-21 | overlay | CI-fixer lives in the product (`githubbot`), not a duplicate overlay watcher. Overlay owns prompts/policy only. |
| 2026-08-07 | agents-flue | Vendor upstream reference clones as **plain tracked files** (no nested `.git`, no submodule) so AGENTS.md pointers work on a vanilla clone. |

---

## 7. Cautionary incidents (what “cleanup” must not do)

These are the anti-patterns the bank recorded after cleanup went wrong.

1. **Hyperdrive cleanup (2026-07-31, blog)** — deleted configs by production-name grouping without checking live Worker bindings. Took down `darkmatter-github-bot` and `iridium-web-production`. *Never delete by name group. Verify live consumers first.*
2. **Cleanup ≠ commit to main (2026-08-10, gitops)** — assistant heard “cleanup approved” and pushed `939db14` to `main`. *Approval of the change is not approval of the land path.*
3. **knip / ts-prune false positives (2026-07-23, web)** — framework peer deps (`react-server-dom-webpack`) look unused. *Grep + know the framework contract before `bun remove`.*
4. **Name-group / leftover scaffolding (2026-06-29, nixmac)** — `ManualCommitStep` survived an incremental unify as leftover. *After a unify, grep for the old name and delete the twin.*
5. **Reserved-for-later knobs (2026-07-19, centaur)** — unused `OutputTooLarge` / `max_exec_output_bytes` misled later readers. *Prefer a clean cutover.*
6. **AGENTS.md override (2026-07-23, web)** — advisory blockers spawned 12 unsolicited agents. *Live user instruction wins.*

---

## 8. Recurring voice (how Cooper actually prompts this)

Compressed from the instances above — the phrases that keep showing up:

- “trim the diff” / “files that did not belong in this commit”
- “audit, repair, and reorganize”
- “remove unused X” / “fails the deletion test” (zero importers)
- “do not Sync / do not recreate”
- “stop all coding”
- “don’t modify production auto/flash”
- “prefer native library conventions; keep customizations thin”
- “short simple names”
- “self-contained packages, not fragmented docs/tests/src”
- “no new services” / “bounded design”
- “clean-slate, replace the overcomplicated implementation”
- “comment the non-obvious contracts”
- “docs are stale”
- “use subagents; you review”
- “surgical” (28-line snapshot, SOPS `set`, ignore-policy jsonPointers)

If a prompt sounds like one of these, it is a maintainability job even when the word “cleanup” never appears.

---

## Method notes

- Bank: `https://api.hindsight.vectorize.io` / `omp`, token `himitsu read hindsight-api-key`.
- Keyword totals are substring hits and include infra “stale pods”, idempotency “dedupe”, etc. The tables above are the **user-ask / standing-rule subset**, not the raw hit list.
- Mental models `user-preferences` and `project-conventions-{agents,gitops,skills,centaur,nixmac}` were treated as distilled standing instructions, not as one-off prompts.
- Nothing was retained back into the bank.
