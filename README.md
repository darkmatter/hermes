# Hermes configuration and skills template

Sanitized configuration and skill bundles for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

## Files

- `config.yaml` configures models, tools, memory, and personalities.
- `SOUL.md` contains an example agent persona.
- `env.example` documents required and optional provider environment variables.
- `skills/` contains the local Hermes skill bundles.
- `profiles/` contains local named profile configuration and skills.
- `devbox/` contains configuration, profiles, and skills sourced from the devbox Hermes home.

## Usage

Copy only the configuration, persona, profile, and skill directories you need into
your Hermes home, then adapt them for your provider, operating system, and
secret-management solution. All credential values, private keys, home paths, and
generated runtime artifacts have been removed or redacted.

## Contributing

This repository is synchronized from its private source of truth. Submit changes
there or open an issue describing a proposed template improvement.

## License

MIT
