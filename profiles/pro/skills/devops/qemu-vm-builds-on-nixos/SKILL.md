---
name: qemu-vm-builds-on-nixos
description: Run Ubuntu (or other Linux) VMs via QEMU/KVM on a NixOS devbox when Docker containers can't provide required kernel-level features like AppArmor, snapd preseeding, or specific LSMs. Covers cloud-image boot, cloud-init seeding, SSH access, and build patterns. Use when a build or tool requires kernel features the NixOS host doesn't have, when snap-preseed fails in Docker, when AppArmor is needed inside a container, or when a full Ubuntu environment is required for building images/packages.
version: 0.1.0
triggers:
  - AppArmor not available in Docker
  - snap-preseed failed
  - chroot verification failed apparmor
  - need full Ubuntu kernel on NixOS
  - QEMU KVM Ubuntu VM
  - cloud-image build environment
  - ubuntu-image on NixOS
  - Docker container missing kernel feature
  - build requires snapd on NixOS
---

# QEMU/KVM Ubuntu VM Builds on NixOS

When a build process requires kernel-level features (AppArmor, snapd preseeding,
specific LSMs, specific kernel modules) that the NixOS host kernel doesn't
provide, Docker containers won't work — they share the host kernel. A QEMU/KVM
Ubuntu VM provides a full independent kernel with all expected features.

## When to Use This Pattern

- **`snap-preseed` fails with `chroot verification failed: cannot preseed without access to .../apparmor`** — snap-preseed requires AppArmor, which NixOS kernels often lack
- **`ubuntu-distro-info` segfaults** inside a Docker container — missing `distro-info-data` package, but also a sign the snap runtime isn't fully functional
- **Build tools need `/sys/kernel/security/apparmor`** — Docker can't mount this if the host kernel doesn't have AppArmor compiled in
- **Any tool that requires a full systemd + snapd + AppArmor stack** — common for Ubuntu image builders, snap-based tools, and chroot customization scripts

## When NOT to Use

- The build only needs userspace packages → use Docker (faster, lighter)
- The NixOS host kernel already has the required feature → check `cat /sys/kernel/security/lsm` first
- The build works in a Docker container with `--privileged` → try that first

## Setup: Install QEMU and cloud-utils on NixOS

```bash
nix profile install nixpkgs#qemu nixpkgs#cloud-utils
# Verify
which qemu-system-x86_64
which cloud-localds
ls -la /dev/kvm  # Should exist with rw permissions
```

## Boot an Ubuntu Cloud Image VM

### 1. Download the Ubuntu cloud image

```bash
mkdir -p ~/vm-build && cd ~/vm-build
curl -sL -o ubuntu-server.img \
  'https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img'
```

### 2. Create a cloud-init seed

Write a `cloud-init.yaml` with your SSH key, packages to pre-install, and any
setup commands:

```yaml
#cloud-config
users:
  - name: builder
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, admin
    home: ~
    shell: /bin/bash
    lock_passwd: false
    plain_text_passwd: builder
    ssh_authorized_keys:
      - <REDACTED>...  # YOUR public key from the host

chpasswd:
  list: |
    builder:builder
    root:builder
  expire: false

ssh_pwauth: true

packages:
  - git
  - curl
  - wget
  - make
  # Add more as needed

runcmd:
  - systemctl enable --now snapd.socket
  - snap install ubuntu-image --classic --edge  # If needed
```

Generate the seed image:

```bash
cp ubuntu-server.img disk.img
cloud-localds seed.img cloud-init.yaml
qemu-img resize disk.img 50G  # Grow the disk
```

### 3. Boot the VM

Use `terminal(background=true, notify_on_complete=true)` — the VM is a
long-lived process that never exits on its own:

```bash
qemu-system-x86_64 \
  -name build-vm \
  -enable-kvm \
  -cpu host -smp 16 -m 32G \
  -drive file=disk.img,format=qcow2,if=virtio \
  -drive file=seed.img,format=raw,if=virtio \
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \
  -device virtio-net-pci,netdev=net0 \
  -nographic \
  -serial file:vm-serial.log \
  -monitor none \
  -pidfile vm.pid
```

Key flags:
- `-enable-kvm -cpu host` — hardware virtualization with host CPU passthrough
- `-smp 16 -m 32G` — adjust based on host resources (devbox has 32 cores, 125GB RAM)
- `hostfwd=tcp::2222-:22` — forward host port 2222 → VM port 22
- `-serial file:vm-serial.log` — capture boot/console output to a file
- `-nographic` — no GUI, serial console only

### 4. Wait for boot and SSH in

```bash
# Watch boot progress
tail -f ~/vm-build/vm-serial.log

# Wait for cloud-init to finish (look for "Cloud-init .* finished")
# Then SSH in (from the NixOS host):
ssh -o StrictHostKeyChecking=no -p 2222 builder@localhost
```

Typical boot time: 30-60 seconds for cloud-init to complete.

### 5. Run builds inside the VM

SSH into the VM and run build commands. For long-running builds, use nohup
inside the VM:

```bash
ssh -p 2222 builder@localhost 'cd ~/project && \
  nohup make build > /output/build.log 2>&1 &'
```

Monitor progress:
```bash
ssh -p 2222 builder@localhost 'tail -20 /output/build.log'
```

### 6. Retrieve build artifacts

```bash
# From the NixOS host, scp from the VM
scp -P 2222 builder@localhost:~/project/result.img ~/result.img

# Or mount a shared directory via 9p (add to QEMU args):
#   -virtfs local,path=~/shared,mount_tag=shared,security_model=none
# Then in the VM:
#   sudo mount -t 9p -o trans=virtio shared /mnt
```

### 7. Shut down the VM

```bash
ssh -p 2222 builder@localhost 'sudo poweroff'
# Or kill the QEMU process if SSH is unavailable:
kill $(cat ~/vm-build/vm.pid)
```

## Pitfalls

- **Docker `--privileged` does NOT give you AppArmor** — the container shares the host kernel. If `cat /sys/kernel/security/lsm` on the host doesn't list `apparmor`, no Docker flag will fix it. Use a VM.
- **`ubuntu-distro-info` segfaults without `distro-info-data`** — the snap bundles its own `ubuntu-distro-info` binary but needs the host's `/usr/share/distro-info/ubuntu.csv`. Install `distro-info-data` in the VM/container before running `ubuntu-image`.
- **`reset` command fails in chroot scripts** — when `ubuntu-image` runs chroot customization scripts non-interactively, `reset` (terminal reset) fails with "No such device or address". Patch scripts to use `reset 2>/dev/null || true`.
- **`in-chroot.sh` git clone overwrites chroot patches** — if you patch a post-chroot script (e.g. `01install-packages.sh`) before building, `in-chroot.sh` does a fresh `git clone https://github.com/tinygrad/tinyos /opt/tinybox` which replaces your patched files. Patch `in-chroot.sh` itself to fix scripts *after* the clone/rsync, e.g. inject a `sed -i` right after the `rsync` line that merges userspace.
- **Makefile `umount efivars` failure** — the tinyos Makefile's cleanup step calls `sudo umount -f result/chroot/sys/firmware/efi/efivars`, which fails if the mount doesn't exist, aborting the build even though the chroot phase succeeded. Fix: run the three `ubuntu-image` phases manually instead of `make green`: (1) `ubuntu-image classic -u perform_manual_customization`, (2) mount chroot fs + `ubuntu-image classic -r -t perform_manual_customization`, (3) unmount + `ubuntu-image classic -r` to finalize.
- **`nohup make` may not find `make`** — the snap-modified PATH may not include `/usr/bin`. Use the full path: `nohup /usr/bin/make green > /output/build.log 2>&1 &`.
- **VM disk too small** — cloud images ship at ~2GB. Always `qemu-img resize` before booting if the build needs space. **120G minimum for full OS image builds** (e.g. tinyos.green.img is 43GB, and `ubuntu-image` duplicates the chroot into a rootfs staging area during `populate_rootfs_contents`, so you need 2× the image size plus overhead). 50G works for smaller builds but will run out of space on large images with CUDA/PyTorch. To resize after booting: shut down VM → `qemu-img resize disk.img 120G` → reboot → `sudo growpart /dev/vda 1 && sudo resize2fs /dev/vda1` (cloud-init may auto-grow, check `df -h`).
- **SSH host key changes on VM rebuild** — use `-o StrictHostKeyChecking=no` or clear `~/.ssh/known_hosts` entries for `[localhost]:2222`.
- **`cloud-localds` requires the cloud-init YAML to be valid** — validate with `cloud-init schema --config-file cloud-init.yaml` if available.
- **SSH timeout on first connect** — cloud-init may still be running. Wait for "Cloud-init.*finished" in the serial log before attempting SSH.

- **`sudo dd` on macOS needs a TTY** — when streaming a build artifact to a USB drive via `dd`, the Mac's `sudo` requires interactive password input. The agent can't provide this in a non-PTY terminal call. Workaround: stream the image to a local file first (no sudo needed), then have the user run `sudo dd` in their own terminal. Alternatively, add `SUDO_PASSWORD` to `~/.hermes/.env` if the agent should handle flashing autonomously.

## Verifying AppArmor is Available

Before starting a build that needs AppArmor, verify inside the VM:

```bash
cat /sys/kernel/security/lsm          # Should list "apparmor"
ls /sys/kernel/security/apparmor      # Should exist
sudo aa-status                        # Should report profiles
```

If these fail, the VM kernel doesn't have AppArmor — use an Ubuntu cloud image (not a custom kernel).

## References

- `references/tinyos-build.md` — Detailed notes on building TinyOS (tinybox green) images, including the ubuntu-image classic workflow, chroot customization phase, and specific patches needed for non-interactive builds.
