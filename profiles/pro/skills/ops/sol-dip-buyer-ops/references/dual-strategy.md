# Dual strategy cutover notes

## Why one-bot-per-market felt broken

Original design: lock + pid keyed to `runs/<mint8>/` so two processes never shared spent ledger.

After cutover:

- Lock/pid are **per `run_id`** under `runs/<mint8>/<run_id>/`
- Default `run_id = <side>-<style>` (e.g. `buy-paint`, `sell-normal`)
- Explicit `--run-id` for custom names (`buy-paint-paper`, `sell-tp`)
- Legacy flat `runs/<mint8>/` still used when that layout already has state and no nested siblings

## Wallet invariant

`enforce_wallet_separation()`:

1. If `--buy-wallet` / `--sell-wallet` opposite annotation equals this side's pubkey → `SystemExit`
2. Scan sibling heartbeats under mint root (legacy + nested); opposite-side same wallet → hard fail
3. Same-side same wallet → warn only (two buy styles on one buy hot wallet OK)
4. Live sell without `--buy-wallet` → warn at start; **hard refuse at fill time** (and botctl gates live sell start)

## Sell path

- TP ladder: `gain:frac` of **current on-chain bag** (not cost basis bag unless paper-no-key ledger)
- Each TP rung recorded in `state.tp_hits` — once per run
- `--stop-loss` → dump up to `--sell-frac-cap` of remaining bag
- `jup_quote` is bidirectional (`inputMint`/`outputMint`); buy uses WSOL→mint, sell mint→WSOL

## botctl arg quirks

- `set -u` safe empty arrays: use `"${ARGS[@]+"${ARGS[@]}"}"` not bare `"${ARGS[@]}"` when optional
- `status` with only `--mint` lists all runs under that mint (not “pick default only”)
- `stop --mint X --all` walks legacy + nested

## Verify checklist (ad-hoc)

```text
py_compile dip_buyer + monitor_check
bash -n scripts/botctl
help exposes --side --run-id --tp-ladder --stop-loss --buy-wallet --sell-wallet
live sell + same --buy-wallet as keypair pubkey → refused
enforce allows distinct BUY_PUB/SELL_PUB; rejects equal
paper --once buy paint + buy absorb + sell under nested run_ids
botctl list shows nested
monitor_check on stopped paper hb → OK
RunLock second acquire → SystemExit
```

## Same strategy on two wallets (verify)

User asked to run **identical paint buy** on padre + marv for verification:

1. `botctl stop --mint $MINT --all` (kill legacy flat run so padre not double-fired)
2. `buy-paint-padre` + `buy-paint-marv` nested run_ids, same style/ref/budget, different `--keypair`
3. Dry wallet → `wallet_low` idle (ok)
4. Not a wash farm — independent ledgers, named keys, no coordinated spoof

Known pubs: padre `GKzKZW…`, marv `PWbrhU…` under `~/wallets/`.

## Non-goals

- Multi-wallet **buy** volume/wash farms (split SOL to N anon wallets + synchronized buys)
- Automatic token handoff buy wallet → sell wallet
- Shared spent coordinator across run_ids (each state file independent)
