# Package consolidation checklist

Use this worksheet when several small workspace packages may belong in one shared library.

## 1. Inventory

For every package, record:

| Field | Questions |
| --- | --- |
| Consumers | Which source files and manifests import it? Are any outside the monorepo? |
| Runtime | Node, browser, edge/Worker, build-time only, or runtime-neutral? |
| Operations | Does it own an app, DB, schedule, deployment, generated binding, or external service? |
| Security | Does it own secrets, permissions, desktop access, SSH, or a distinct trust boundary? |
| Compatibility | Does it pin a dependency version that conflicts with likely siblings? |
| Assets | Does it load encrypted JSON, Markdown, Python, native binaries, or files by relative path? |
| Surface | What are its exports? Is there a cohesive independent public contract? |
| Evidence | Is separation needed now, or only imagined for future reuse? |

Measure source/test size and imports to inform the review, but never use line count alone as the decision.

## 2. Classify

Use one of three outcomes:

- **Application-local:** one runnable app consumes it and it is inseparable from that runtime.
- **Shared-library section:** multiple internal consumers, no independent operational or compatibility boundary.
- **Independent package:** concrete version, runtime, security, infrastructure, release, ownership, or external-consumer boundary.

Small packages may remain independent when package resolution itself is the contract, such as shared TypeScript or lint configuration.

## 3. Design the shared package

Prefer explicit exports:

```json
{
  "name": "@repo/lib",
  "exports": {
    "./models": "./src/models/index.ts",
    "./utils": "./src/utils/index.ts"
  }
}
```

Avoid `".": "./src/index.ts"` unless the package truly has one unified API. Use relative imports between sections:

```ts
import { clampInteger } from "../utils/index.ts";
```

Do not make the package depend on itself through `@repo/lib/*`.

## 4. Write the red architecture test

Assert the desired package roots and exports before moving files. Include negative assertions for:

- old package directories;
- old package names in manifests and source;
- root barrels when prohibited;
- accidental removal of packages that should stay independent;
- deployment files appearing inside reusable library packages.

Run it and confirm the failure is caused by the old structure, not a test bug.

## 5. Move safely

1. Move source and tests without changing behavior.
2. Preserve filename-relative imports or update them deliberately.
3. Merge package dependencies and reconcile version pins.
4. Change internal cross-section imports to relative paths.
5. Update source imports to explicit subpaths such as `@repo/lib/models`.
6. Update manifests separately: dependency keys use the package root `@repo/lib`, never a subpath. Deduplicate runtime/dev entries when several old packages collapse into one.
7. Update generator templates and architecture documentation.
8. Handle path-sensitive assets explicitly.
9. Regenerate the lockfile only after workspace manifests are final.

For SOPS or another authenticated encrypted file, use its CLI to move/edit data and verify decryption afterward; never hand-edit ciphertext metadata or the MAC.

## 6. Verify

- Architecture test green.
- New package targeted typecheck and tests green.
- No moved suite disappeared from test discovery.
- All consumer packages typecheck.
- Repository-wide static and offline test gates pass.
- Every runnable app builds.
- Inspect real generated output when scanners/bundlers synthesize identities, bindings, or manifests.
- Smoke the built runtime when safe.
- Search for old imports, manifests, path aliases, and forwarding packages.
- Frozen lockfile install passes.
- Diff/whitespace check passes.

Do not infer bundle safety from TypeScript. Explicit subpath exports help, but only a real build proves that Node-only or optional dependencies did not leak into an edge artifact.

## 7. Graduation record

When extracting a section later, document the concrete reason: version conflict, external consumer, operational/security boundary, distinct ownership, independent replacement, or material dependency cost. “It got larger” is supporting evidence, not a boundary by itself.
