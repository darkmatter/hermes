# Streamflow lock on padre (top bag)

## When

Cooper locks MARV for optics (“top holder locked so people don’t panic”) while optionally keeping a sell drip.

## Platform

**[Streamflow](https://app.streamflow.finance/)** — default. Self-lock recipient = padre (or cold). Token-2022 mint OK if selected correctly.

Do it from **padre** (`GKzKZW…`) if the story is top-holder lock — not mrv/mrv2/dip.

## Interaction with `sell-absorb-padre`

- Sell bot sizes from **free ATA** only (`getTokenAccountsByOwner`).
- Lock moves tokens into Streamflow escrow → **free bag shrinks** (e.g. ~540M → ~340M).
- Drip continues on unlocked sleeve; full lock → `bag_empty` / idle sell.
- Leave unlocked pants if slow sell should keep running.

## Ops checklist

1. Pause or accept reduced free bag before locking most inventory.
2. Connect padre carefully (import keypair into wallet UI — never paste into chat).
3. After lock: `spl-token balance` free ATA + heartbeat `token_ui` / `remaining_tokens` should match unlocked only.
4. Public Streamflow contract link is fine to show the dev; don’t doxx other identities.
