# Kernel computer use (AA / similar booking UIs)

Cooper correction: when agent-browser or DOM fill fails AA passenger, **use Kernel computer use** (screenshot + click/type), not more agent-browser fill.

## Driver
```bash
export KERNEL_API_KEY=<REDACTED>
```
Use himitsu key load as usual. Then:
```bash
SID=<session>
kernel browsers computer screenshot "$SID" --to /tmp/aa.png
kernel browsers computer click-mouse "$SID" --x N --y N
kernel browsers computer type "$SID" --text '…' --delay 20
kernel browsers computer scroll "$SID" --x 720 --y 450 --delta-y 400
kernel browsers computer press-key "$SID" --key PageDown
```

## Vision
Coords from `vision_analyze` on the PNG. If vision crashes with DaemonThreadPoolExecutor `_initializer`, **fix that** (Py3.14 daemon_pool) — do not invent another weak fill path. Overlay: `$HOME/.local/lib/hermes-py314-fix` — see `python314-daemon-pool-vision.md`.

## AA pax checklist
- Open “Enter new passenger”
- Name / DOB / gender / country / **state (CA)**
- Email/phone on contact Fields only
- Leave **loyalty blank** unless program chosen (never stash phone in loyalty)
- Email is `telvaya@icloud.com` for Telavaya (not pelavaya)
- Screenshot after Save before Continue
- Pay only after Cooper OK

## Live link
Always later have `kernel browsers view` URL ready when Cooper says “give me link”; after expire, recreate and only link once back at the same step.
