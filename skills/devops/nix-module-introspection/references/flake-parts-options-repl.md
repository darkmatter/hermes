# Validated flake-parts options inspection

This example was exercised against a consumer flake importing
`inputs.prelude.flakeModules.default` through flake-parts.

## Zero-edit Prelude query

```console
$ nix repl
nix-repl> :lf .
nix-repl> p = inputs.flake-parts.lib.mkFlake { inherit inputs; } {
             imports = [ inputs.prelude.flakeModules.default ];
             debug = true;
             systems = [ ];
           }
nix-repl> builtins.attrNames p.debug.options.prelude
[
  "colorProfile"
  "commands"
  "docs"
  "menu"
  "motd"
  "palette"
  "project"
  "prompt"
  "sort"
  "theme"
]
```

Leaf metadata queries returned:

```console
nix-repl> p.debug.options.prelude.theme.description
"Color theme for all prelude components."

nix-repl> p.debug.options.prelude.theme.type.description
"one of \"amber\", \"apathy\", \"gruvbox\", \"minted\", \"mono\", \"nord\", \"paper\", \"phosphor\", \"prelude\", \"solarized\""

nix-repl> p.debug.options.prelude.theme.default
"minted"
```

## Why it works

flake-parts' debug module adds these flake outputs when `debug = true`:

- `debug`: top-level `config`, `options`, `_module`, and `extendModules`;
- `allSystems.<system>`: the same information for the evaluated `perSystem`
  submodule;
- `currentSystem`: an impure convenience shortcut when available.

Evaluating the input module in a fresh `mkFlake` isolates its declared schema
from the consumer's local option assignments.

## Browse Prelude's generated reference

Prelude ships generated option documentation in its locked source:

```sh
preludePath="$(nix flake archive --json . | jq -r '.inputs.prelude.path')"
less "$preludePath/docs/reference/options.md"
```

The consumer's `nix run .#docs` command launches Prelude's project-document
viewer. It is useful for configured docs pages but is not itself a generic
module-schema inspector; use the evaluated `debug.options` tree for exact
schema data.
