---
name: solana-memecoin-dd
description: "Due-diligence for Solana memecoins (Pump.fun and graduations): coin metadata, market snapshot, mint authorities, creator bag, and verifying whether 'dev locked' claims are real on-chain locks (Streamflow etc.) vs UI theater. Use when the user pastes a pump.fun mint, asks if the dev is locked, wants holder/LP risk, or reviews a just-launched Solana meme."
---

# Solana memecoin DD (Pump.fun + locks)

Fast, evidence-first checklist. Prefer on-chain / primary APIs over scraper UIs (GMGN/Solscan often Cloudflare-block server IPs).

## Triggers
- Pump.fun mint (`…pump`) or support link
- "Is the dev locked?", "check lock", "rugcheck", "creator bag"
- Quick mcap / LP / authority scan on a new Solana meme
- "TWAP" / "absorb dips" / scale-in buy on a thin Pump graduate (read sizing rules — usually **not** a time TWAP)

## Output shape (default)
Lead with **verdict**, then a tight table of proofs (accounts + tx sigs + flag values). Call out what the lock does **not** cover (float, fees, cliff dump). Skip long narrative unless asked.

## Execution / sizing (when user wants to buy)
Do **not** blind-TWAP into Pump AMM liquidity. Treat buy intent as **dip ladder / dry-powder** unless they explicitly accept impact.

1. **Refresh live LP** (DexScreener `liquidity.quote` = pool SOL) before any size discussion.
2. **Impact back-of-envelope** (constant product, quote side ≈ pool SOL): clips above ~2–3% of pool SOL move price hard; ≥ pool SOL is specialist/toxic.
3. If user names a huge budget (e.g. 100 SOL) vs ~tens of SOL LP: budget = **ceiling / dry powder**, not one TWAP notional. Prefer drawdown triggers + cooldown + $/hour cap + per-clip pool-frac cap.
4. HL habits do not map 1:1 — Solana AMMs have no resting bid ladder; each “level” is a marketable swap that moves the pool.
5. Trading keys: Cooper often funds via **Padre**, stores export in himitsu as **`sol-1`** (czxtm/secrets). Materialize with `himitsu exec sol-1 -- python …` (injects secret as env matching `sol-1` / `SOL_1` patterns → base58 64-byte → `Keypair.from_bytes`) to `~/wallets/padre-sol-1.json` chmod 600. Print **pubkey + balance only**. Unused empty scaffold wallets can be ignored once Padre is wired.
6. Default ops mode: paper/signals or scaffold only; require dedicated hot wallet + explicit arm for live. Scaffold: `~/git/darkmatter/sol-dip-buyer/` (multi-mint via **`--mint` required**; styles `absorb|normal|paint`).
7. **Never run long-lived live bot as a foreground agent tool session.** Use detached controller so the chat can die without killing fills:
   ```bash
   cd ~/git/darkmatter/sol-dip-buyer
   ./scripts/botctl start --mint <MINT> --live --confirm-live YES --style paint --ref-mcap 100000 --budget 99
   ./scripts/botctl status|logs|stop --mint <MINT>
   ./scripts/monitor_check.py --mint <MINT>   # cron: exit 1 if dead/stale
   ```
   Per-run artifacts under `runs/<mint8>/<run_id>/` (default `run_id=<side>-<style>`; legacy flat `runs/<mint8>/` still ok). Files: `bot.pid`, `bot.lock` per run, `heartbeat.json`, `bot.log`, `state.json`, `trades.csv`. Heartbeat stale if mtime > `stale_after_s` (~30s). Multi-strategy: `botctl status --mint $MINT` / `monitor_check.py --mint $MINT --all`.
8. **Style lever:** when user wants the chart to *look* defended (“paint”, green recovery on dips), do **not** stay on silent absorb — raise pool-frac / clip / hour caps, use impact-target sizing, and say impact is the point. Absorb/normal stay low pool-frac. See `references/dip-entry-sizing.md` (lever map).
9. **Clip size** = SOL per single buy, not budget. Explain once if they ask “what’s clip size?”.
10. **Ref can be a market-cap target**, not only spot. Prefer bot `--ref-mcap N` (converts via live `mcap/price` supply; fallback 1B). Rule of thumb still `ref_usd ≈ mcap/1e9` on standard pump supply. When ref ≫ live spot, deepest rung stays armed → buys every cooldown until caps — say that before arming.
11. **“Not buying / not moving price” triage (in order):** (1) is a **live** process actually running (`botctl status`)? (2) is spot ≥ first ladder rung under ref (paint first rung **−8%**)? (3) cooldown / hourly / budget caps? (4) impact levers too small (`--target-impact`, `--max-pool-frac`, `--max-clip`)? This is a **dip ladder**, not continuous bid-up — rubber-hose staircase needs a different mode, not just higher clip.
12. **Switch wallets freely:** user does **not** have to send into a scaffold address. Any funded key → himitsu/keyfile → `DIP_BUYER_KEYPAIR` / `--keypair` is fine. Prefer exportfonder wallet they already financed (Padre) over creating dead intermediate addresses.
13. **Hard refuse multi-wallet wash/split farms** (funder→N wallets→coordinated buys to spoof volume). **OK:** same buy strategy on multiple *named* hot wallets with separate `run_id`s for size/verify; buy≠sell on different accounts. Full bot ops: skill **`sol-dip-buyer-ops`** (class-level — do not fold botctl runbooks into this DD skill).
14. Never imply lock quality makes size safe; lock DD and entry sizing are separate answers.

**Boundary:** this skill = evidence-first **due diligence** on a mint. Live multi-strategy paint/sell/ref-ramp operation of `~/git/darkmatter/sol-dip-buyer` is **`sol-dip-buyer-ops`**.

See `references/dip-entry-sizing.md`.

## Workflow

### 1. Coin + market snapshot
```bash
MINT=<mint>
curl -sS "https://frontend-api-v3.pump.fun/coins/$MINT" | jq .
curl -sS "https://api.dexscreener.com/latest/dex/tokens/$MINT" | jq .
curl -sS "https://api.rugcheck.xyz/v1/tokens/$MINT/report" -o /tmp/rug.json
```
Record: name/symbol, `complete` (graduated?), creator, created/ATH/last trade times, PumpSwap pool, mcap, liq, buy/sell imbalance, boosts.

Note: many `/holders`, `/trades`, `user-created-coins` routes on `frontend-api-v3` 404 — do not depend on them.

### 2. Mint safety (RPC)
Token-2022 is common on current Pump mints (`TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`).
```bash
# getAccountInfo jsonParsed on mint → mintAuthority, freezeAuthority, extensions
# getTokenAccountsByOwner on creator + mint → residual creator balance
```
Good: authorities `null`, metadata update authority burned/null, no transfer fee / permanent delegate surprises (rugcheck `token_extensions`).

### 3. "Is the dev locked?" / "When does rc unlock?" — do not trust UI badges

**Answer shape for unlock timing:**
1. If Streamflow (or similar) vest found → report **cliff/end UTC+local**, cancelable flags, escrow remaining, deep link.
2. If **no** vest/lockers after try **and** creator ATA has free tokens → **"no public dev unlock date; free float can sell anytime"** (state residual bag + SOL).
3. Always answer **LP lock/burn separately** from **dev-token vest** — users conflate them.
4. Rugcheck `lockers: {}` / `lockerScanStatus: none` is **insufficient alone** — still scan creator sigs for `strmRq…` Create (see pitfalls).

**Order of evidence:**
1. Creator wallet signatures (`getSignaturesForAddress`)
2. Find lock program invoke (Streamflow first — see below)
3. Decode metadata account with official layout
4. Confirm escrow token account still holds the full deposited amount
5. Creator residual ATA + SOL (unlocked inventory)
6. Separately check **LP** lock/burn (migration), which is not the same as dev-token vest

#### Streamflow (most common pump "dev lock")
- Program: `strmRqUCoQUgGUan5YhzUZa6KqdzwX5L6FpUxfmKg5m`
- Log markers: `Instruction: Create`, `Initializing SPL token stream`, `Moving funds into escrow`
- Create ix account order (js-sdk):
  `sender`, `sender_tokens`, `recipient`, `metadata`, `escrow_tokens`, `recipient_tokens`, …
- **Self-vest** is normal: `sender == recipient == creator` (tokens still locked if flags say so).
- Layout source of truth: Streamflow js-sdk `packages/stream/solana/layout.ts` (`streamLayout`) — see `references/streamflow-lock-decode.md`.
- Must report all of:
  - `net_amount_deposited` / escrow UI balance
  - `start_time`, `cliff`, `end_time`, `period`, `amount_per_period`, `cliff_amount`
  - **`cancelable_by_sender` / `cancelable_by_recipient`** (both must be 0 for a hard lock)
  - `transferable_by_sender/recipient`, `pausable`, `can_update_rate`, `canceled_at`, `withdrawn_amount`
- Unlock shape cheat-sheet:
  - `amount_per_period == net` and cliff at +period → **100% cliff** (single unlock), not a drip
  - Linear vest when `amount_per_period` is a slice and end > cliff

Pump creator allocation is typically **1%** (10M of 1B UI units). Streamaway often locks ~all of it; **creator ATA dust (thousands of tokens) ≠ unlocked bag**.

Streamflow app deep link:
`https://app.streamflow.finance/contract/solana/mainnet/<metadata>`

#### LP after Pump graduation
- Rugcheck market `pump_fun_amm`: `lp.lpLockedPct`, `lpUnlocked`, LP mint `supply`
- Pump migration normally **burns LP** (`lp mint supply == 0`, locked pct 100). That stops LP pull, not holder dumps.

### 4. Creator fee path (not a token unlock)
Creator can still `CollectCreatorFee` / `CollectCoinCreatorFee` on Pump + pAMM while tokens are locked. Check recent creator sigs; fee cash ≠ vest unlock.

### 5. Holders / concentration
Rugcheck `topHolders` (owner field distinguishes pool vs wallets). Flag pool as non-insider. Insider graphs optional.

## Pitfalls
- **UI "LOCKED" without escrow balance check** — always read Streamflow metadata + escrow ATA.
- **Cancelable self-vest** — if `cancelable_by_sender=1`, treat as **not locked**.
- **Transferable stream** — sender can reassign recipient; call it out.
- **Hard cliff dump** — non-cancelable 30d 100% cliff is real lock *until* cliff, then full creator supply can hit book. Session proof (MARV): 30d full-amount cliff, cancel flags 0, escrow still full.
- **LP burn ≠ dev locked** — answer both separately when user asks "is the dev locked?".
- **Rugcheck empty lockers ≠ no Streamflow** — `lockers: {}` / `lockerOwners: {}` still common; always scan creator sigs for `strmRq…` Create.
- **Creator fee path still live** — Pump `CollectCreatorFee` / pAMM `CollectCoinCreatorFee` can fire while vest is locked; fee cash ≠ token unlock.
- **Blind TWAP on graduated pump** — schedule-only large SOL vs thin pool chases strength and wrecks exits; preferred path is **dip ladder**. If user *wants* visible green paint on dips, that is intentional impact sizing of dip buys — not the same as blind full-notional TWAP.
- **Budget vs deployable** — "eventually spend entire balance" still needs pool-frac + hourly caps (higher under paint); full deploy may take many dip episodes or never.
- **Mcap ref always in profit zone** — pinning ref at 100k while spot is 5k mcap means ~95% drawdown forever → bot hammers deepest rung every cooldown until hour/budget caps. Reconfirm that is intended when user sets “ref = 100k market cap”.
- **Bot idle = often “process stopped”** — after agent session botctl stop/paper smoke, nothing buys. Check `botctl status` before tuning levers. Live must be detached (`botctl start`), not an agent foreground shell that dies with the turn.
- **Not continuous bid-up** — dip ladder only fires below ref rungs. “Make it drift up now while above first rung / with bot stopped” is a different product; don’t only raise `--target-impact`.
- **Multi-wallet wash farm** — refuse. Multi *named* hot wallets same buy strategy (separate run_ids) or buy≠sell split = OK; see `sol-dip-buyer-ops`.
- **Wallet mobility** — switching to any funded keyfile is fine; empty scaffold deposit addresses can be abandoned once Padre/`sol-1` is live.
- **Himitsu/Padre keys** — materialize `sol-1` via `himitsu exec` to a 600 keyfile; confirm on-chain balance before arming; never echo seed/key into chat or logs.
- **State file mint mismatch** — each coin gets its own `runs/<mint8>/state.json`; bot refuses reuse across mints. Old root `live-state.json` is legacy leftover — don’t mix spent with new run dirs without explicit carry-forward.
- **Cloudflare / 401** on GMGN, Solscan HTML, Birdeye free — fall back to public RPC + pump API + dexscreener + rugcheck.
- **Public Solana RPC 429** — space `getTransaction` / largest-accounts calls; retry with backoff.
- **Do not install solders just to b58** — tiny pure-Python b58 or `base58` is enough for layout decode.
- **argparse help strings** — avoid raw `%` in help (use "percent"); Python 3.14 raises on badly formed help.
- **Jupiter lite quote/swap** — `https://lite-api.jup.ag/swap/v1/quote` + `/swap` works for Pump.fun AMM routes without a paid key (still need user keypair to send).

## References
- `references/streamflow-lock-decode.md` — account layout offsets, field meanings, decode recipe
- `references/api-endpoints.md` — stable HTTP/RPC endpoints used in this workflow
- `references/dip-entry-sizing.md` — TWAP vs dip-ladder, style levers, detached botctl, “why idle” triage
- `references/sol-dip-buyer-ops.md` — copy-paste start/status, budget remainder, Prelude entry, lever map

## Project DX (Prelude)
Repo is Prelude-flavored for operator UX (not required for raw botctl):
```bash
cd ~/git/darkmatter/sol-dip-buyer
nix develop            # MOTD + menu/docs/x + botctl on PATH
# or: direnv allow
menu | docs | x bot:live-help | x bot:paper-once | x bot:status
```
Flake pieces: `flake.nix` (inputs `github:darkmatter/prelude`), `prelude.nix` (MOTD/menu/docs), `title.txt`, `docs/{getting-started,operations}.md`, `.envrc`. Prefer documenting operator flows in prelude commands (`x bot:live-help`) so live paste commands are not buried in chat history.

When adding Prelude to other small Python/tooling repos: template from `github:darkmatter/prelude#default` / native’s `prelude.nix` split — thin `flake.nix` imports module + `./prelude.nix`; register `fromPkg` wrappers that `cd` to repo root via `SOL_DIP_ROOT`/`git`/`dip_buyer.py` marker (store-path wrappers are not the project root). See `references/sol-dip-buyer-ops.md`.

## Budget carry-forward
If a prior live session already spent `S` of an original ceiling `B`, arm with `--budget (B - S)` (e.g. 99 − 6.49 → **92.51**). Do not double-credit old root `live-state.json` into a fresh `runs/<mint8>/` without explicit transfer — new run dir starts spent=0 unless you seed it.

## Related
- Broader chain analytics SQL: `dune` skill (Sim/API) when historical multi-token queries needed beyond a single-mint DD.
- Local dip bot (detached ops + Prelude): `~/git/darkmatter/sol-dip-buyer/` — `scripts/botctl`, `scripts/monitor_check.py`, `nix develop`
- `references/sol-dip-buyer-ops.md` — copy-paste statuses, lever map, live start template
