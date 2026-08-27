# Composio SDK Script Execution Pitfalls

When executing stand-alone TypeScript scripts that depend on `@composio/core`:

1. **Directory Context:** Run scripts within an initialized Node project folder (where `package.json` resides). Avoid running them from a scratch directory like `/tmp` unless you have run `npm install` there, else the module loader will complain `Error: Cannot find module '@composio/core'`.
2. **Installation:** If staging in a new directory, run `npm install @composio/core @composio/openai-agents @openai/agents --legacy-peer-deps`.
3. **Module Type:** Include `"type": "module"` in package.json as top-level await fails with CJS output format in tsx.
