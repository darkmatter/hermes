#!/usr/bin/env bash
# Verify Prelude→Helix theme ports under ~/darwin and optional live install.
set -euo pipefail

THEMES_DIR="${THEMES_DIR:-$HOME/darwin/files/helix/themes}"
HELIX_NIX="${HELIX_NIX:-$HOME/darwin/modules~/helix.nix}"
LIVE_DIR="${LIVE_DIR:-$HOME/.config/helix/themes}"
names=(phosphor minted amber solarized nord gruvbox mono apathy paper prelude)
fail=0

echo "== presence =="
for t in "${names[@]}"; do
  [[ -f "$THEMES_DIR/prelude-$t.toml" ]] || { echo "MISSING source prelude-$t"; fail=1; }
  if [[ -d "$LIVE_DIR" ]]; then
    [[ -f "$LIVE_DIR/prelude-$t.toml" ]] || echo "warn: not live yet prelude-$t"
  fi
done
echo "ok source themes checked"

echo "== helix.nix =="
if [[ -f "$HELIX_NIX" ]]; then
  nix-instantiate --parse "$HELIX_NIX" >/dev/null
  for t in "${names[@]}"; do
    rg -q "prelude-$t" "$HELIX_NIX" || { echo "MISSING list prelude-$t"; fail=1; }
  done
  rg -q 'preludeThemes' "$HELIX_NIX" || { echo "MISSING preludeThemes"; fail=1; }
  echo "ok parse + wiring"
else
  echo "warn: no helix.nix at $HELIX_NIX"
fi

echo "== palette anchors/refs =="
python3 - <<'PY'
from pathlib import Path
import os, re, sys
themes_dir = Path(os.environ.get("THEMES_DIR", Path.home() / "darwin/files/helix/themes"))
names = "phosphor minted amber solarized nord gruvbox mono apathy paper prelude".split()
required = {
    "bg","gutter","panel","surface","cursorline","selection","search","border",
    "fg","muted","dim","invisible","accent","accent2","success","warning","info","error","selection_fg",
}
anchors = {
    "phosphor": {"bg": "#0c110e", "accent": "#68e371", "fg": "#d5e2d7"},
    "minted": {"bg": "#0c0c13", "accent": "#f2cdcd", "accent2": "#CC99FF"},
    "paper": {"bg": "#f4f2ec", "accent": "#1e7729", "fg": "#252a27"},
    "prelude": {"bg": "#0e0b13", "accent": "#ff87d7", "error": "#ff005f"},
    "apathy": {"bg": "#0e0b13", "accent": "#77f5c9", "accent2": "#ffcb6b"},
}
rc = 0
for name in names:
    path = themes_dir / f"prelude-{name}.toml"
    if not path.is_file():
        print("MISSING", path); rc = 1; continue
    text = path.read_text()
    pal = text.split("[palette]", 1)[1]
    keys = set(re.findall(r"^([a-z0-9_]+)\s*=", pal, re.M))
    vals = dict(re.findall(r'^([a-z0-9_]+)\s*=\s*"([^"]+)"', pal, re.M))
    if required - keys:
        print("FAIL keys", name, required - keys); rc = 1
    if any(not re.fullmatch(r"#[0-9a-fA-F]{6}", v) for v in vals.values()):
        print("FAIL hex", name); rc = 1
    refs = set(re.findall(r'(?:fg|bg|color) = "([a-z0-9_]+)"', text))
    if refs - keys:
        print("FAIL refs", name, refs - keys); rc = 1
    for k, v in anchors.get(name, {}).items():
        if vals.get(k, "").lower() != v.lower():
            print("FAIL anchor", name, k, vals.get(k), v); rc = 1
print("ok palettes" if rc == 0 else "palette failures")
sys.exit(rc)
PY

if command -v hx >/dev/null 2>&1; then
  echo "== helix load =="
  TMP=$(mktemp -d "${TMPDIR:-/tmp}/verify-hx-themes.XXXXXX")
  export XDG_CONFIG_HOME="$TMP" XDG_CACHE_HOME="$TMP/cache"
  mkdir -p "$TMP/helix/themes" "$TMP/cache/helix"
  cp -f "$THEMES_DIR"/prelude-*.toml "$TMP/helix/themes/"
  cp -f "${HOME}/.config/helix/languages.toml" "$TMP/helix/" 2>/dev/null || true
  for t in "${names[@]}"; do
    name="prelude-$t"
    printf 'theme = "%s"\n[editor]\ntrue-color = true\n' "$name" > "$TMP/helix/config.toml"
    LOG="$TMP/cache/helix/helix.log"; rm -f "$LOG"
    printf ':q\n' | timeout 2 hx "$TMP/helix/config.toml" >/dev/null 2>&1 || true
    if [[ -f "$LOG" ]] && rg -i 'theme|failed to load|unknown|error parsing' "$LOG" >/dev/null; then
      echo "FAIL load $name"; rg -i 'theme|failed|unknown|error' "$LOG" | head -5; fail=1
    else
      echo "ok load $name"
    fi
  done
  rm -rf "$TMP"
else
  echo "warn: hx not on PATH; skipped load test"
fi

[[ $fail -eq 0 ]] && echo "RESULT: PASS" || { echo "RESULT: FAIL"; exit 1; }
