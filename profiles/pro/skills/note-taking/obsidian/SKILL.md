---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `${HERMES_HOME:-~/.hermes}/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

**Pitfall — env var unset AND fallback missing.** When `OBSIDIAN_VAULT_PATH` is unset and `~/Documents/Obsidian Vault` does not exist, do not give up or guess a path. Discover actual vaults by searching for `.obsidian` directories under the home dir:
```
find ~ -maxdepth 4 -name '.obsidian' -type d 2>/dev/null
```
The **parent** of a `.obsidian` dir is the vault root. This environment commonly has **multiple** vaults (e.g. a personal vault at `~/personal` and a team/project vault such as `~/git/<org>/obsidian`). When more than one is returned, pick the right vault by **content**, not by position: a `20-work/weekly-updates/` folder (or a top-level `Wiki/` tree) signals a team status vault; `Tweet Drafts/` signals a personal vault; an `ADR-` / `Wiki/` tree signals an engineering wiki. If a task spans two vaults, read from both and keep them straight — never assume a single vault.

**Pitfall — guessing folder placement inside a vault.** Once you've picked a vault, don't drop a note at the root or in a guessed folder. Many team vaults use a PARA-style numbered layout with their own `VAULT_GUIDE.md` stating where each note type lives. For the darkmatter team vault (`~/git/darkmatter/obsidian`), the authoritative guide is `_system/VAULT_GUIDE.md` (older copy at `_archive/VAULT_GUIDE.md`) — read it before placing a note. Condensed layout in `references/team-vault-layout.md`. Example: weekly team updates go in `20-work/weekly-updates/YYYY-MM-DD.md` (plain name, no suffix); daily notes in `20-work/daily-notes/`; durable knowledge under `Wiki/`. Do not write to the deprecated flat `Weekly/` folder at vault root.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
