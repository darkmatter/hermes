# Darkmatter Team Vault Layout

Vault root: `~/git/darkmatter/obsidian` (git-synced; Obsidian sync disabled). Authoritative placement rules live in the vault's own `_system/VAULT_GUIDE.md` — read that when in doubt; this file is a condensed mirror.

## PARA-style numbered layout

| Folder | Holds |
|---|---|
| `00-inbox/` | Uncertain / captured notes awaiting sorting |
| `20-work/` | Active work artifacts |
| `20-work/weekly-updates/` | Weekly team status updates — `YYYY-MM-DD.md`, plain name, no suffix |
| `20-work/daily-notes/` | Daily notes — `YYYY-MM-DD.md` |
| `Wiki/` | Durable team knowledge (Company, People, Product, Engineering, Operations, Teams, Reference) — publishable |
| `60-agents/` | Reusable agent assets (skills, prompts) |
| `70-publishing/` | Editorial / publication work |
| `90-personal/` | Personal working notes (per-user subfolders) |
| `_system/` | Templates, assets, bases, scripts, styles; `Weekly Update.md` template lives here |
| `_archive/` | Completed / inactive material |

## Conventions observed

- Weekly updates: `20-work/weekly-updates/YYYY-MM-DD.md` (NOT `Weekly/…-darkmatter-weekly.md`). The flat `Weekly/` folder at vault root is deprecated/empty — do not write there.
- Frontmatter: weekly updates use the `_system/templates/Weekly Update.md` template (`title`, `date`, `publish: false`, `visibility: internal`, `tags: [blog]`).
- Publishing: a note is eligible for publishing only with both `visibility: public|internal` and `publish: true`. Wiki pages go under top-level `Wiki/`.
- A git-push plugin auto-pushes after edits; a manual push once confirms it works.

## Sibling crons that read/write here

- **Weekly Dark Matter Team Update** cron (`91271c7fd0f3`, Mon 9am) writes `20-work/weekly-updates/YYYY-MM-DD.md`.
- **Weekly review** cron (`6cd57f56a22d`, Sun 6pm) reads those files as input (see the `weekly-review` skill). Both must stay path-aligned — a drift in the writer's save path breaks the consumer silently.
