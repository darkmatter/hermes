# Hermes configuration and skills template

Sanitized configuration and skill bundles for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

## Files

- `config.yaml` configures models, tools, memory, and personalities.
- `SOUL.md` contains an example agent persona.
- `env.example` documents required and optional provider environment variables.
- `skills/` contains the local Hermes skill bundles.
- `profiles/` contains local named profile configuration and skills.
- `devbox/` contains configuration, profiles, and skills sourced from the devbox Hermes home.
- `nix/modules/nixos/hermes-server.nix` composes the official Hermes NixOS module
  with an optional dashboard, shared skills, and Cloudflare Tunnel connector.

## Usage

Copy only the configuration, persona, profile, and skill directories you need into
your Hermes home, then adapt them for your provider, operating system, and
secret-management solution. All credential values, private keys, home paths, and
generated runtime artifacts have been removed or redacted.

## NixOS server

Import both the official Hermes NixOS module and
`nix/modules/nixos/hermes-server.nix`, then configure
`services.hermesServer`. The module intentionally does not manage DNS, firewall
rules, Cloudflare account resources, or secrets. Provide dashboard and tunnel
credentials through your own SOPS, Agenix, or equivalent generated
`EnvironmentFile`s.

## Contributing

This repository is synchronized from its private source of truth. Submit changes
there or open an issue describing a proposed template improvement.

## License

MIT
