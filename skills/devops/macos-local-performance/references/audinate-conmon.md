# Audinate Dante ConMon on Cooper's Mac

## Identity

- Binary: `conmon_cmm` (often misread as container `conmon`)
- Path: `/Library/Application Support/Audinate/ConMon.bundle/Contents/MacOS/conmon_cmm`
- Launchd: `com.audinate.dante.ConMon`
- Plist: `/Library/LaunchDaemons/com.audinate.dante.ConMon.plist`
- Package: `com.audinate.dante.conmon.pkg` (seen as v402.0.4 / bundle 4.2.0)
- Install observed: 2026-03-06
- Log: `/Library/Logs/Audinate/conmon.log`

ConMon is Audinate's **Dante network audio discovery / connection monitor**. It is **not** required for ordinary Universal Audio Thunderbolt interface → speakers.

## UA vs Dante

| Stack | Role | Keep for speakers? |
|---|---|---|
| UA Thunderbolt device + driver | Local I/O | Yes |
| `com.uaudio.*`, UA Mixer Engine, UAD Console/Meter | Apollo/Console routing | Yes when using UA |
| Audinate ConMon | Dante AoIP discovery | **No** unless using Dante devices/DVS/Via |

Cooper's typical path: default output **Universal Audio Thunderbolt**, monitor PA27DCE, mic HyperX SoloCast — local TB/USB, not Dante.

## Permanent disable (done 2026-08-07)

```bash
sudo launchctl bootout system /Library/LaunchDaemons/com.audinate.dante.ConMon.plist 2>/dev/null || true
sudo launchctl disable system/com.audinate.dante.ConMon
sudo launchctl print-disabled system | rg audinate
# expect: "com.audinate.dante.ConMon" => disabled
pgrep -lf conmon_cmm || echo gone
```

Files left on disk for reverse. Bootstrap while disabled should fail.

### Re-enable

```bash
sudo launchctl enable system/com.audinate.dante.ConMon
sudo launchctl bootstrap system /Library/LaunchDaemons/com.audinate.dante.ConMon.plist
```

### Full uninstall (optional, only if never using Dante)

```bash
sudo "/Library/Application Support/Audinate/ConMon.bundle/Contents/Resources/delete.sh" 2>/dev/null || true
sudo rm -rf "/Library/Application Support/Audinate"
sudo rm -f /Library/LaunchDaemons/com.audinate.dante.ConMon.plist
sudo pkgutil --forget com.audinate.dante.conmon.pkg
```

Do **not** remove UA software when only killing ConMon.

## Symptom pattern

- Near-constant ~1 core (`~90–100%` on one thread)
- Huge cumulative CPU time (days of uptime → hundreds of hours)
- Appears next to `kernel_task` in casual `ps` reads → easy to mis-blame the kernel
