---
name: effect-typescript
description: Use when TypeScript/Bun code involves meaningful I/O and you are writing, reviewing, or deciding whether to use Effect, especially services, Layers, Config, Schema, typed errors, retries, resources, tests, or Alchemy deployments.
---

# Effect TypeScript

Use Effect deliberately. The most important trigger is meaningful I/O: external APIs, files, databases, queues, workers, CLIs, config, secrets, clocks, subprocesses, network calls, or deployable runtime boundaries. Effect is excellent when that I/O needs typed failures, dependencies, runtime validation, retries, concurrency, resources, and testable boundaries. It is not a default replacement for simple TypeScript.

This skill adapts guidance from `effect-smol` to darkmatter conventions: use Bun commands instead of pnpm, and prefer Alchemy for deployable infrastructure.

## When to use

- Meaningful I/O is involved and the work benefits from explicit failure, dependency, resource, retry, validation, or testing boundaries.
- The code already uses Effect and you are adding or reviewing Effect code.
- You are deciding whether a TypeScript/Bun feature should use Effect.
- The task involves external APIs, databases, queues, workers, CLIs, schedules, retries, config, secrets, structured logging, runtime validation, resource cleanup, or concurrent workflows.
- You need typed domain errors rather than unstructured thrown exceptions.
- You need swappable live/test implementations through services and Layers.
- You are deploying TypeScript infrastructure or workers and need Alchemy-aware conventions.

## When NOT to use

- A small one-off script can be obvious plain TypeScript: read one file, transform pure data, write one file, no retries, no injected dependencies, no long-lived resources.
- Pure functions, simple data mappers, UI-local state, or tiny glue code do not need Effect wrappers.
- A project has no Effect dependency and the feature does not benefit from typed errors, Layers, resource safety, retries, or observability.
- The team only needs a tactical fix in plain async code. Do not introduce Effect as a drive-by refactor.
- You cannot explain the service/layer/error/testing shape. Stop and design that first instead of sprinkling `Effect.runPromise` calls everywhere.

## Decision Rule

Use Effect when at least two of these are true:

- There are multiple effectful dependencies to compose.
- Failures need to be represented in types and handled by tag.
- Inputs or outputs cross trust boundaries and need `Schema` validation.
- There are retries, timeouts, schedules, or polling.
- There are resources with lifecycle: DB pools, clients, sockets, subscriptions, background fibers.
- Tests need fake services, shared layers, `TestClock`, or deterministic concurrency.
- The runtime is long-lived: worker, server, daemon, queue consumer, scheduled job.

If only one is true, prefer plain TypeScript unless the surrounding codebase already uses Effect.

## Darkmatter Conventions

- Use Bun commands: `bun install`, `bun test`, `bun run <script>`, `bunx <tool>`.
- Translate upstream `pnpm` examples mechanically. Example: `pnpm test file.test.ts` becomes `bun test file.test.ts` when the project uses Bun test, or `bun run test file.test.ts` when test is a package script.
- Prefer Bun runtime packages where relevant, such as `@effect/platform-bun` and `BunRuntime.runMain` for Bun entrypoints.
- Prefer Alchemy for deployable infrastructure. Put infra in `alchemy.run.ts`, create resources with Alchemy, bind them to workers/services, and call `await app.finalize()`.
- Do not bake secrets into code or Alchemy resources. Use environment variables and `alchemy.secret(...)` for secret bindings.
- Keep application logic independent from Alchemy. Alchemy owns infrastructure wiring; Effect services own runtime behavior.

## Core Patterns

### Program Shape

- Keep pure logic as plain functions.
- Put effectful operations in `Effect` values.
- Use `Effect.gen` for inline effect composition.
- Use `Effect.fn("Name")` for exported or reusable functions returning Effects; name it after the function for traces.
- In low-level hot library code, `Effect.fnUntraced` is acceptable when tracing overhead matters.
- Attach behavior with combinators: `Effect.catchTag`, `Effect.retry`, `Effect.withSpan`, `Effect.annotateLogs`, `Effect.provide`.

```ts
import { Effect, Schema } from "effect"

class InvalidPayload extends Schema.TaggedErrorClass<InvalidPayload>()(
  "InvalidPayload",
  { message: Schema.String }
) {}

export const parsePayload = Effect.fn("parsePayload")(function*(input: string) {
  if (input.length === 0) {
    return yield* new InvalidPayload({ message: "payload is empty" })
  }
  return JSON.parse(input) as unknown
})
```

### Services and Layers

Use `Context.Service` for dependencies. Put the live implementation on `static readonly layer`, and expose test layers separately.

```ts
import { Context, Effect, Layer, Schema } from "effect"

class ApiError extends Schema.TaggedErrorClass<ApiError>()("ApiError", {
  message: Schema.String,
  cause: Schema.Defect
}) {}

export class UsersApi extends Context.Service<UsersApi, {
  readonly getUser: (id: string) => Effect.Effect<unknown, ApiError>
}>()("app/UsersApi") {
  static readonly layer = Layer.effect(
    UsersApi,
    Effect.gen(function*() {
      const getUser = Effect.fn("UsersApi.getUser")((id: string) =>
        Effect.tryPromise({
          try: () => fetch(`https://example.com/users/${id}`).then((r) => r.json()),
          catch: (cause) => new ApiError({ message: "failed to fetch user", cause })
        })
      )

      return UsersApi.of({ getUser })
    })
  )
}
```

Layer rules:

- `Layer.effect(Service, Effect.gen(...))` for effectful construction.
- `Layer.succeed(Service, impl)` for pure/static implementations.
- `Layer.unwrap(effectReturningLayer)` when choosing a layer from `Config` or another Effect.
- Compose layers at the boundary, not inside business logic.
- Use `ManagedRuntime` only to bridge Effect into non-Effect frameworks or callbacks. Create one runtime from the application layer and dispose it on shutdown.

### Errors

- Model expected failures as tagged errors, preferably with `Schema.TaggedErrorClass`.
- Use `_tag`-aware handlers: `Effect.catchTag` or `Effect.catchTags`.
- Preserve unknown causes with `cause: Schema.Defect` or an explicit field.
- Do not throw for expected domain failures.
- When a branch terminates inside `Effect.gen`, use `return yield*` so TypeScript understands control flow.

```ts
if (notFound) {
  return yield* new UserNotFound({ id })
}
```

### Config and Secrets

- Use `Config.string`, `Config.boolean`, `Config.url`, and `Config.redacted` instead of reading `process.env` throughout the codebase.
- Decode config once in layers, then expose typed services to the rest of the app.
- Use `Config.withDefault` for safe non-secret defaults.
- Keep secrets redacted in logs and errors.

### Schema

- Use `Schema` for data crossing trust boundaries: HTTP requests, API responses, queue payloads, config-like JSON, AI outputs, and persisted data.
- Prefer schema classes for domain entities that move across modules.
- Decode unknown external data before it enters core business logic.
- Do not use `as SomeType` to silence unknown JSON from external systems.

### Retries, Schedules, and Time

- Use `Schedule` with `Effect.retry` for transient failures.
- Make retryability explicit in the error type, such as `retryable: boolean`.
- Add caps and jitter for production retries.
- Use `Clock` in Effect code and `TestClock` in tests. Avoid `Date.now()` and `new Date()` in Effectful logic unless you are deliberately at a non-Effect edge.

```ts
const retryPolicy = Schedule.exponential("250 millis").pipe(
  Schedule.recurs(5),
  Schedule.jittered
)
```

### Resources and Scope

- Use `Effect.acquireRelease` for resources that must be closed.
- Put resource acquisition in a Layer so consumers do not manage lifecycle manually.
- Use scoped or launched layers for long-running background work.
- Do not start detached fibers unless detached lifetime is truly intended.

### Running Programs

- At Bun entrypoints, prefer `BunRuntime.runMain(program)` from `@effect/platform-bun`.
- For long-running service layers, use `Layer.launch(AppLayer)` as the process entrypoint.
- For framework handlers or callbacks, use `ManagedRuntime.make(AppLayer)` once, call `runtime.runPromise(...)` at the edge, and dispose on shutdown.
- Do not call `Effect.runPromise` deep inside library or service code. Run Effects at the application boundary.

## Testing

- Use `@effect/vitest` for Effect tests when available.
- Use `it.effect` for Effect-based tests.
- Use regular `it` for pure functions.
- In `it.effect`, use `assert` helpers instead of Vitest `expect`.
- Do not use `Effect.runSync` inside tests.
- Use `TestClock` for time-dependent code.
- Test services through Layers. Provide fake/test layers rather than mocking internals.
- For shared expensive setup, use `layer(...)` from `@effect/vitest`; otherwise provide a test layer per test for isolation.

```ts
import { assert, it } from "@effect/vitest"
import { Effect } from "effect"

it.effect("uses a service", () =>
  Effect.gen(function*() {
    const service = yield* UsersApi
    const user = yield* service.getUser("123")
    assert.isObject(user)
  }).pipe(Effect.provide(UsersApi.layer))
)
```

## Alchemy Deployment

Use Alchemy for infrastructure definitions, especially Cloudflare workers and bound resources.

```ts
// alchemy.run.ts
import alchemy from "alchemy"
import { Worker } from "alchemy/cloudflare"

const app = await alchemy("my-app")

export const worker = await Worker("api", {
  entrypoint: "./src/worker.ts",
  bindings: {
    STAGE: app.stage,
    API_KEY: <REDACTED>
  }
})

console.log({ url: worker.url })
await app.finalize()
```

Alchemy rules:

- Use `alchemy.run.ts` as the default infra entrypoint.
- Run Alchemy with Bun: `bunx alchemy dev`, `bunx alchemy deploy`, `bunx alchemy deploy --stage production`, `bunx alchemy destroy`.
- Always call `await app.finalize()` so orphaned resources are reconciled.
- Use `Cloudflare.state()` as the state store for Cloudflare stacks, including local development and tests. Do not switch to filesystem/local state just because a stack runs locally.
- Toggle local Worker execution with Alchemy's dev mode (`bunx alchemy dev`, test harness `dev: true`, or `ALCHEMY_DEV=1`), not by changing the state backend. See the Alchemy local dev docs: https://v2.alchemy.run/tutorial/part-4/
- Bind infrastructure resources into the runtime environment; then adapt those bindings into Effect services at the worker/app boundary.
- Keep deploy state and resource names stage-aware. Avoid hard-coded production names in shared examples.
- Do not hide application logic in `alchemy.run.ts`; keep it in `src/` and test it independently.

## Review Checklist

- Is Effect justified, or would plain TypeScript be clearer?
- Are pure functions left pure?
- Are expected failures typed and handled by tag?
- Is unknown data decoded with `Schema` before use?
- Are dependencies modeled as `Context.Service` and provided by Layers?
- Are resources acquired/released safely?
- Are retries bounded, jittered, and limited to retryable errors?
- Are Effects run only at the boundary?
- Are tests using `it.effect`, Layers, and `TestClock` where appropriate?
- Are commands written for Bun rather than pnpm?
- Is deployable infra expressed with Alchemy and finalized?
- Do Cloudflare stacks keep `Cloudflare.state()` while using dev mode for local execution?

## Common Mistakes

- Introducing Effect for a tiny script with no real effect-system benefits.
- Wrapping every helper in `Effect.succeed` instead of keeping pure code pure.
- Using `try/catch` inside `Effect.gen` for Effect failures. Use Effect error combinators.
- Throwing strings or generic `Error` for expected domain errors.
- Using `Data.TaggedError` in new code when `Schema.TaggedErrorClass` is available; coexist with older code when needed, but prefer schema-backed errors for new boundaries.
- Forgetting `return yield*` on terminal failures.
- Calling `Effect.runPromise` inside services instead of at the edge.
- Reading `process.env` in many places instead of using `Config`.
- Retrying every failure, including validation and authorization errors.
- Using real time in tests instead of `TestClock`.
- Copying upstream `pnpm` commands into darkmatter projects instead of adapting to Bun.
- Deploying Cloudflare or AWS resources ad hoc instead of encoding them in Alchemy.
- Replacing `Cloudflare.state()` with filesystem/local state for local dev or PR previews; use Alchemy dev mode instead.
