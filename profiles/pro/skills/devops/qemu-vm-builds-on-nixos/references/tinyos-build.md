# TinyOS (TinyBox) Image Build Notes

Notes from building `tinyos.green.img` for a TinyBox Green factory reset.

## Background

The TinyBox Green is Tiny Corp's (George Hotz / tinygrad) 6× RTX 4090 AI server.
Its OS — "TinyOS" — is a custom Ubuntu 24.04 image built from the
[`tinygrad/tinyos`](https://github.com/tinygrad/tinyos) repo.

### Key repos

| Repo | Purpose |
|------|---------|
| `tinygrad/tinyos` | OS image builder. `make green` → `tinyos.green.img` |
| `tinygrad/tinyos-takeover` | Netboot image that auto-flashes tinyos to a tinybox's internal drive |
| `tinygrad/tinybox` | Scripts and environment for the tinybox (fan control, GPU reset, etc.) |

### Recovery mechanism (tinyos-takeover)

Tiny Corp's official recovery tool is **tinyos-takeover** — a minimal Nix-built
netboot image (bzImage + initrd). When booted on a tinybox, it:
1. Detects hardware (NVIDIA = Green, AMD = Red)
2. Downloads the correct `tinyos.green.img` from `http://192.168.52.180:11001/tinyos/`
   (a **private** Tiny Corp internal server — not publicly accessible)
3. Flashes it to the internal drive via `dd`
4. Fixes GPT headers (`sgdisk -e`), sets UEFI boot entries (`efibootmgr`), reboots

This is **netboot-only** (PXE). There is no public download of either the
tinyos image or the takeover netboot artifacts.

### Contact for pre-built images

- **Email**: support@tinygrad.org
- **Discord**: https://discord.com/invite/ZjZadyC7PK
- **X**: @__tinygrad__ or @realGeorgeHotz

## Building tinyos.green.img

### Requirements

- Ubuntu 24.04 (or VM) with:
  - `snapd` + `ubuntu-image` snap (`sudo snap install ubuntu-image --classic --edge`)
  - `distro-info-data` package (provides `/usr/share/distro-info/ubuntu.csv`)
  - `make`, `git`, `curl`
  - **AppArmor must be active** (required by `snap-preseed`)
- ~120GB free disk space (the image is ~43GB, but ubuntu-image duplicates the
  chroot during `populate_rootfs_contents`, needing 2× the image size)
- Does NOT work on macOS or NixOS directly (needs Ubuntu kernel with AppArmor)

### Build steps

```bash
git clone https://github.com/tinygrad/tinyos.git
cd tinyos
make green    # builds tinyos.green.img
```

### What `make green` does

1. Substitutes template variables in `tinyos.template.yaml` (artifact name, Ubuntu series)
2. Writes `TINYBOX_COLOR=green` to `build/tinybox-release`
3. Runs `ubuntu-image classic --debug -w result -u perform_manual_customization tinyos.yaml`
   — builds the image up to the manual customization step (steps 0-8: gadget tree,
   germinate, create chroot, upgrade/install packages, prepare image, preseed snaps)
4. Mounts proc/sys/dev/pts into the chroot
5. Runs `ubuntu-image classic --debug -w result -r -t perform_manual_customization tinyos.yaml`
   — executes `in-chroot.sh` which:
   - Runs pre-scripts: set release file, create `tiny` user, set locale
   - Clones tinyos repo into chroot at `/opt/tinybox`
   - Merges userspace files into `/`
   - Runs post-scripts: install packages (gum, nix, uv, llvm-21), install NVIDIA
     drivers + CUDA, install PyTorch, install tinygrad, build venv, set up services
6. Unmounts chroot filesystems
7. Runs `ubuntu-image classic --debug -w result -r tinyos.yaml` — finalizes the image
8. Outputs `result/tinyos.green.img`

### Green-specific driver installation

From `build/in-chroot-post.d/02install-drivers.sh`:
- Installs CUDA keyring from `developer.download.nvidia.com`
- Installs NVIDIA kernel module from `wozeparrot/open-gpu-kernel-modules` GitHub
  releases (version 570.211.01-p2p — a patched fork with P2P support)
- Installs `nvidia-driver-570-open`, `cuda-toolkit-12-8`, `cuda-drivers-570`
- Holds all NVIDIA packages to prevent auto-upgrade

### Image structure

- Based on Ubuntu 24.04 (Noble) with HWE kernel
- EFI-bootable (GRUB + shim-signed)
- Uses `ubuntu-image classic` with `pc-gadget` (standard PC gadget)
- Cloud-init for first-boot setup (`firstsetup.sh` — interactive setup wizard)
- Includes: tinygrad, PyTorch, CUDA 12.8, NVIDIA 570 drivers, nix, uv, btop,
  ripgrep, direnv, ipmitool, lm-sensors, and more

## Pitfalls encountered during build

### 1. AppArmor required by snap-preseed

**Error**: `chroot verification failed: cannot preseed without access to
".../sys/kernel/security/apparmor"`

**Cause**: NixOS host kernel doesn't have AppArmor compiled in. Docker
containers share the host kernel, so `--privileged` doesn't help.

**Fix**: Use a QEMU/KVM Ubuntu VM (which has its own kernel with AppArmor).

### 2. `ubuntu-distro-info` segfault

**Error**: `Error: unable to get distro info: signal: segmentation fault (core dumped)`

**Cause**: The `ubuntu-distro-info` binary bundled in the ubuntu-image snap
needs `/usr/share/distro-info/ubuntu.csv`, which isn't installed by default.

**Fix**: `apt-get install distro-info-data`

### 3. `reset` command fails in chroot

**Error**: `reset: terminal attributes: No such device or address` → build fails

**Cause**: `build/in-chroot-post.d/01install-packages.sh` calls `reset` after
installing nix. In a non-interactive chroot (no TTY), `reset` fails.

**Fix**: Patch the script: `sed -i 's/^reset$/reset 2>\/dev\/null || true/'`

### 4. Missing `tinybox-release` in chroot

**Error**: `cp: cannot stat '/opt/tinybox/build/tinybox-release': No such file
or directory`

**Cause**: When resuming a partially-completed build with `ubuntu-image -r`,
the `build/tinybox-release` file (written by `make green`) may not have been
copied into the chroot's `/opt/tinybox/build/` directory.

**Fix**: `sudo cp build/tinybox-release result/chroot/opt/tinybox/build/tinybox-release`

### 5. `make` not found in nohup

**Error**: `nohup: failed to run command 'make': No such file or directory`

**Cause**: When running `nohup make` inside an SSH session, the snap-modified
PATH may not include `/usr/bin` where `make` lives.

**Fix**: Use full path: `nohup /usr/bin/make green > /output/build.log 2>&1 &`

### 6. Disk space exhaustion during `populate_rootfs_contents`

**Error**: `cp: cannot create regular file '...': No space left on device` during
the final `ubuntu-image classic -r` phase.

**Cause**: `ubuntu-image` copies the entire chroot (result/chroot → result/root)
to stage the rootfs before making the disk image. This means you need space for
both the chroot AND its copy — roughly 2× the final image size. A 43GB tinyos
image needs ~120GB of disk space during the build.

**Fix**: Shut down VM → `qemu-img resize disk.img 120G` → reboot → verify with
`df -h /`. Cloud-init may auto-grow the partition; if not, run
`sudo growpart /dev/vda 1 && sudo resize2fs /dev/vda1`.

### 7. Makefile `umount efivars` failure

**Error**: `umount: result/chroot/sys/firmware/efi/efivars: no mount point
specified.` → `make[1]: *** [Makefile:92: image] Error 32`

**Cause**: The Makefile's cleanup step tries to unmount efivars, but it was
never mounted (or was already unmounted). This aborts the build even though
the chroot customization ("Build successful" appears in the log).

**Fix**: Don't use `make green` directly. Run the three `ubuntu-image` phases
manually:

```bash
# Phase 1: build up to manual customization
sudo ubuntu-image classic --debug -w result -u perform_manual_customization tinyos.yaml

# Mount chroot filesystems
sudo mount -t proc proc result/chroot/proc
sudo mount -t sysfs sysfs result/chroot/sys
sudo mount -o bind /dev result/chroot/dev
sudo mount -t devpts devpts result/chroot/dev/pts

# Phase 2: run manual customization (chroot phase)
sudo ubuntu-image classic --debug -w result -r -t perform_manual_customization tinyos.yaml

# Unmount
sudo umount -f result/chroot/proc result/chroot/sys result/chroot/dev/pts result/chroot/dev

# Phase 3: finalize the image
sudo ubuntu-image classic --debug -w result -r tinyos.yaml
```

### 8. `in-chroot.sh` git clone overwrites patches

**Error**: You patch `01install-packages.sh` to fix `reset`, but the fix is
lost because `in-chroot.sh` does `git clone https://github.com/tinygrad/tinyos
/opt/tinybox` which replaces your patched files.

**Fix**: Patch `in-chroot.sh` itself to inject the fix *after* the clone+rsync:

```python
# Add after the rsync line in build/in-chroot.sh:
sed -i 's/^reset$/reset 2>\/dev\/null || true/' /opt/tinybox/build/in-chroot-post.d/01install-packages.sh
```

## Flashing the image to USB

Once `tinyos.green.img` is built (43GB for green):

### Option A: Direct dd on the VM host (if USB is attached to the VM host)

```bash
# On the VM (or host if image is transferred there):
sudo dd if=tinyos.green.img of=/dev/sdX bs=16M oflag=direct status=progress
```

### Option B: Stream over SSH to Mac (no intermediate disk needed)

If the image is on the VM and the USB is on the Mac, pipe directly over SSH
to avoid needing 43GB of free disk on the Mac or devbox:

```bash
# On macOS — unmount the USB first
diskutil unmountDisk /dev/disk24

# Stream: VM → devbox → Mac → USB (gzip compressed over network)
ssh devbox "ssh -p 2222 builder@localhost 'sudo gzip -c ~/tinyos/result/tinyos.green.img'" \
  | gunzip | sudo dd of=/dev/rdisk24 bs=16m

diskutil eject /dev/disk24
```

**Note**: Use `/dev/rdisk24` (raw device) not `/dev/disk24` — raw writes are
significantly faster on macOS.

### Option C: Stream to local file, then dd (recommended)

If the agent doesn't have passwordless sudo on the Mac (common), the direct
streaming pipeline (Option B) will fail because `sudo dd` needs a TTY for the
password. Instead, stream to a local file (no sudo needed), then have the user
run the `dd` command:

```bash
# 1. Stream the image to a local file (no sudo needed — ~15 min over gigabit)
ssh devbox "ssh -p 2222 builder@localhost 'sudo gzip -1 -c ~/tinyos/result/tinyos.green.img'" \
  | gunzip > /tmp/tinyos.green.img

# 2. Verify the file size matches (~43GB for green)
ls -lh /tmp/tinyos.green.img

# 3. Flash to USB (REQUIRES sudo — user runs this in their terminal)
diskutil unmountDisk /dev/disk24
sudo dd if=/tmp/tinyos.green.img of=/dev/rdisk24 bs=16m
diskutil eject /dev/disk24
```

**Note**: Use `gzip -1` (fastest compression level) for the streaming approach —
the bottleneck is network/disk I/O, not CPU, so minimal compression reduces
latency. Use `/dev/rdisk24` (raw device) not `/dev/disk24` — raw writes are
significantly faster on macOS.

**Sudo on the VM**: The VM's `sudo` also needs to be passwordless for the
streaming pipeline. If cloud-init didn't set it up, run once via interactive SSH:
```bash
ssh -t devbox "ssh -t -p 2222 builder@localhost 'echo \"builder ALL=(ALL) NOPASSWD: ALL\" | sudo tee /etc/sudoers.d/builder'"
```

### Option D: Direct scp then dd

```bash
# Transfer the image to the Mac (slower than gzip streaming — no compression)
scp devbox:~/tinyos.green.img ~/tinyos.green.img

# Flash
diskutil unmountDisk /dev/disk24
sudo dd if=tinyos.green.img of=/dev/rdisk24 bs=16m
diskutil eject /dev/disk24
```

## Booting the TinyBox from USB

1. Insert USB drive into the TinyBox Green
2. Power on
3. Enter BIOS boot menu (likely Del, F11, F12, or F2 during POST)
4. Select the USB drive
5. The tinyos image boots into the first-setup wizard (interactive setup via
   VGA monitor + keyboard, or via BMC IPMI serial console)

### BMC access (headless)

If no monitor is available, use the BMC (IPMI):
```bash
ipmitool -H <BMC_IP> -U admin -P <BMC_PW> -I lanplus sol activate
```
Default credentials: user `tiny`, password `tiny`.
