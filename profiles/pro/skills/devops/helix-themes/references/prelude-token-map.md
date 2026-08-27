# Prelude → Helix token map

Source: `~/git/darkmatter/prelude/src/prelude/themes.nix`

## Themes (as of port session)

| Prelude name | Helix theme id | Notes |
|--------------|----------------|--------|
| phosphor | `prelude-phosphor` | green phosphor CRT |
| minted | `prelude-minted` | indigo + rose/lilac (not the same as hand-tuned `apathy-minted`) |
| amber | `prelude-amber` | warm amber mono-ish fg |
| solarized | `prelude-solarized` | teal-dark solarized-inspired |
| nord | `prelude-nord` | prefix required (built-in `nord`) |
| gruvbox | `prelude-gruvbox` | prefix required (built-in gruvbox variants) |
| mono | `prelude-mono` | grayscale hierarchy |
| apathy | `prelude-apathy` | mint accent + butterscotch; distinct from rich `apathy.toml` |
| paper | `prelude-paper` | **light** theme — invert surface derivation |
| prelude | `prelude-prelude` | brand pink/lime; `secondary` is chrome gray not a panel |

## Tokens (every theme)

```
bg surface secondary fg muted dim border accentBorder
accent accent2 success warning info error selectionFg
```

Helix palette keys used by generated ports:

```
bg gutter panel surface cursorline selection search border
fg muted dim invisible accent accent2 success warning info error selection_fg
```

## Derivation rules (generator)

Dark:

- `gutter` ← darken(bg, ~0.18)
- `panel` ← mix(bg, surface, ~0.55)
- `cursorline` ← mix(bg, secondary, ~0.35)
- `selection` ← secondary (except brand prelude)
- `search` ← mix(surface, accent2, ~0.22)
- `invisible` ← mix(bg, dim, ~0.45)

Light (paper):

- slight darken of bg for gutter; mix toward secondary for selection/cursorline

Brand prelude:

- `selection` ← mix(surface, accent, ~0.25)
- `panel` ← surface
- `cursorline` ← mix(bg, surface, ~0.65)

## Darwin install list

`modules~/helix.nix` → `preludeThemes` must stay in sync with files named `prelude-*.toml` under `files/helix/themes/`.
