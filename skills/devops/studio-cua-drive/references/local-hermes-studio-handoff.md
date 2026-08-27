# Local Studio Hermes handoff

## Verified topology

The Studio is reachable at `coopers-mac-studio` over Tailscale. On the Pro, `tailscale ping coopers-mac-studio` returned a pong from `100.111.149.47`, and SSH verbose output showed the same Tailnet address. The Pro Hermes config can use an SSH stdio MCP bridge:

```yaml
mcp_servers:
  cua-driver:
    command: ssh
    args:
      - -o
      - BatchMode=yes
      - -o
      - StrictHostKeyChecking=yes
      - coopermaruyama@coopers-mac-studio
      - ~/.local/bin/cua-driver
      - mcp
```

`hermes mcp test cua-driver` discovered 49 tools.

## Studio readiness check

On the Studio, Hermes may already be installed while still lacking a model/provider or MCP configuration. Installation is not readiness. Run without printing secrets:

```bash
hermes --version
hermes status --all
hermes config path
hermes mcp list
hermes mcp test cua-driver
```

A local agent is ready only when model/auth status is usable and the local CuaDriver MCP test discovers its tools.

## Target local configuration

The preferred final topology is local Hermes plus local CuaDriver plus local Chrome:

```yaml
mcp_servers:
  cua-driver:
    command: ~/.local/bin/cua-driver
    args: [mcp]
    enabled: true
```

Do not copy the Pro session database, OAuth state, `.env`, or secret files implicitly. Keep non-secret config in the Darwin/Home Manager repository and render credentials at activation time from agenix/sops or the approved local secret store. Never commit rendered credentials.

## Nix/macOS deployment

Hermes' official Nix guidance treats macOS as a package/profile installation target; the NixOS service module is for NixOS, not nix-darwin. In a nix-darwin repo that already packages Hermes, add the local config through the Studio Home Manager host and point it at the local CuaDriver binary. Keep the direct MCP entry declarative.

Useful verification pattern:

```bash
nix build --no-link --fallback \
  '.#homeConfigurations.coopermaruyama@coopers-mac-studio.activationPackage'
```

If the full Darwin system build is blocked by an unrelated package, the Home Manager activation package can be built separately and activated from its output path. Treat activation as successful only if the command exits zero; reaching `linkGeneration` or a custom activation step before a later package error is partial application, not a complete deployment.

After activation, verify:

```bash
readlink "$HOME/.hermes/config.yaml"
hermes mcp list
hermes mcp test cua-driver
```

## Handoff rule

Use the SSH/Tailscale bridge only when the active Hermes session remains on the Pro. For payment and browser work, the preferred final topology is local Studio Hermes plus local CuaDriver plus local Chrome. Kernel remains a fallback, not a parallel first choice. Preserve the Pro session until the Studio agent passes model/auth, config, and MCP health checks.
