# Vision / concurrent tools crash on Python 3.14

## Symptom
```
Error during OpenAI-compatible API call: 'DaemonThreadPoolExecutor' object has no attribute '_initializer'
```
Breaks `vision_analyze`, many file tools on Hermes TUI when agent runs under **Python 3.14**.

## Cause
- Hermes TUI: nix `hermes-agent` on **3.14.6**.
- `tools/daemon_pool.py` mirrored CPython **3.8–3.13** workers: passes `self._initializer`.
- **3.14** removes that attr; worker signature is `(ref, worker_context, work_queue)` via `_create_worker_context()`.

## Fix shape (class-level)
`DaemonThreadPoolExecutor._adjust_thread_count`:
- if `hasattr(self, "_create_worker_context")` → 3.14+ args
- else → legacy `_initializer` / `_initargs`

## Where fixed in this ops environment
- Overlay: `~/.local/lib/hermes-py314-fix/tools/daemon_pool.py`
- Checkout: `~/.hermes/hermes-agent/tools/daemon_pool.py `
- Nix: `darwin/patches/daemon_pool.py` + postPatch/postInstall on hermes-agent
- Helper: `hermes-tui-py314fix` sets `PYTHONPATH` to overlay

## Activate without full rebuild
Restart TUI with:
```bash
PYTHONPATH="$HOME/.local/lib/hermes-py314-fix${PYTHONPATH:+:$PYTHONPATH}" hermes --tui
```

## Verification
```bash
# should FAIL without overlay on stock 3.14 hermes site-packages
# should OK with PYTHONPATH overlay: submit → 1
```

## Policy when vision fails
**Diagnose/fix the tool path.** Do not silently replace with weaker drive loops “because vision failed.” If vision is required for computer-use coords, stop booking and fix executor/path first.
