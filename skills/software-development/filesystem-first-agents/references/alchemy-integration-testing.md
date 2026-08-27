# Alchemy integration testing for Flue infrastructure

Use this after unit tests, typecheck, and the Flue/Vite build pass. Those checks do **not** prove that Alchemy can deploy the Worker/DO/Container graph.

## Required audit

Before calling an Alchemy-backed prototype complete, search its tests for:

```text
alchemy/Test
Test.make
beforeAll(deploy(Stack))
afterAll(destroy(Stack))
```

If no harness exists, report the Alchemy integration as **not yet tested**, even when the resource classes typecheck and the prebuilt Worker artifact is valid.

## Pinned Effect-native harness

For versions exposing `alchemy/Test/Bun`:

```ts
import * as Cloudflare from "alchemy/Cloudflare";
import * as Test from "alchemy/Test/Bun";
import * as Effect from "effect/Effect";
import Stack from "../alchemy.run.ts";

const { test, beforeAll, afterAll, deploy, destroy } = Test.make({
  providers: Cloudflare.providers(),
  state: Cloudflare.state(),
  stage: "test",
});

const stack = beforeAll(deploy(Stack));
afterAll(destroy(Stack));

test("deploys the composed worker graph", Effect.gen(function* () {
  const outputs = yield* stack;
  // Assert stable Worker/host outputs and exercise fixed smoke behavior.
}));
```

Verify the installed package exports before copying this shape; Alchemy v2 beta APIs move quickly.

## Coverage requirements

The integration suite should prove:

1. The Alchemy sandbox host Worker and Container deploy.
2. The prebuilt Flue Worker uploads as a module graph without rebundling.
3. Every scanner-generated Flue Durable Object binding exists and Alchemy owns its SQLite migration.
4. The cross-script `Sandbox` namespace resolves from the Flue Worker.
5. Cron bindings match the Worker handler's declared expressions.
6. Stack outputs identify the expected resources and provide a bounded health probe.
7. Cleanup destroys the test stage by default.

## Safety and suite placement

- Keep real-cloud tests opt-in (for example `test:alchemy`) instead of silently mixing them into offline Vitest suites.
- Destruction is the default. A `NO_DESTROY` escape hatch is only for explicit debugging, never the normal CI path.
- Do not add an unauthenticated arbitrary-command HTTP endpoint just to test sandbox RPC. Use a test-only probe Worker or a fixed-operation smoke method.
- Use a deterministic test stage; never randomize production-like physical names.
- Never print secrets or include them in stack outputs.

## Monorepo command surface

Expose cloud integration tests at both the deployable app and repository root. Developers naturally run tests from the monorepo root; an app-only script makes a valid suite look missing.

```json
// apps/<deployable-app>/package.json
{
  "scripts": {
    "test:alchemy": "bun run build && RUN_ALCHEMY_INTEGRATION=1 bun test ./test/alchemy_bun_test_.ts",
    "test:alchemy:offline": "bun test ./test/alchemy_bun_test_.ts"
  }
}

// root package.json
{
  "scripts": {
    "test:alchemy": "bun run --cwd apps/<deployable-app> test:alchemy",
    "test:alchemy:offline": "bun run --cwd apps/<deployable-app> test:alchemy:offline"
  }
}
```

Triage in this order:

1. If root output is `Script not found "test:alchemy"`, inspect both `package.json` files; this is a command-surface defect, not an Alchemy/provider failure.
2. Add the root forwarding script and verify it with `bun pm pkg get scripts.test:alchemy scripts.test:alchemy:offline`.
3. Run the root `test:alchemy:offline` command. It may report `0 pass / 1 skip`; that proves command resolution and helper loading, **not** cloud deployment.
4. Run the live command only with explicit authorization because it provisions and destroys real resources.

Bun recognizes `_test_` filenames, while Vitest's default `*.test.*` / `*.spec.*` discovery does not. A name such as `alchemy_bun_test_.ts` keeps an opt-in Bun suite out of both app-local and root Vitest runs without relying solely on one package's Vitest exclude list.

## Version-bound compatibility checks

Do not trust a broad peer range as proof of runtime compatibility. A validated failure mode for `alchemy@2.0.0-beta.57` is:

- its peer range admits Effect beta.84 and newer;
- it still calls `Schedule.both`;
- Effect beta.102 removed that API;
- importing `alchemy/Test/Bun` therefore fails before any test executes.

For that exact version combination, the working containment is to pin only the Alchemy-facing app and reusable infrastructure package to `effect@4.0.0-beta.84`, leaving the rest of the monorepo on its newer Effect catalog version. Bun then installs a peer-qualified Alchemy instance for beta.84. Verify the actual symlink/package resolution and run repository-wide typechecks and tests; do not downgrade the whole workspace reflexively. Reinspect installed source when either version changes.

## Cross-script Durable Object class shape

When a namespace must be bound from another Worker with `Namespace.from(HostWorker)`, use Alchemy's modular class-plus-Live shape:

```ts
export class Sandbox extends Cloudflare.DurableObjectNamespace<Sandbox, Shape>()(
  "Sandbox",
) {}

export const SandboxLive = Sandbox.make(implementation);

export class SandboxHost extends Cloudflare.Worker<SandboxHost, {}, Sandbox>()(
  "SandboxHost",
  props,
) {}

export const SandboxHostLive = SandboxHost.make(
  hostImplementation.pipe(Effect.provide(SandboxLive)),
);
```

Provide `SandboxHostLive` to the stack and bind with `Sandbox.from(SandboxHost)`. An inline default implementation can typecheck locally yet omit the static cross-script `.from(...)` surface needed by deployment composition.

## Evidence standard

Source inspection, generated-config assertions, typecheck, and a successful Flue build are prerequisites. Only a live Alchemy test-helper deploy (or an equivalent explicitly verified deployment) is evidence that cross-script DO bindings, Container attachment, migrations, and cleanup work together.
