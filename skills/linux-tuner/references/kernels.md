# Kernel & Distro Packages Reference

## CachyOS Kernels (Arch-based only)

Packages (all in CachyOS repo or via `cachyos-kernel-manager`):

| Package | Scheduler | sched_ext? | Notes |
|---------|-----------|-----------|-------|
| `linux-cachyos` | BORE | Yes | Default, recommended starting point |
| `linux-cachyos-bore` | BORE | Yes | Explicit BORE build |
| `linux-cachyos-eevdf` | EEVDF | Yes | Stock upstream scheduler |
| `linux-cachyos-bmq` | BMQ/PDS | No | Incompatible with sched_ext |
| `linux-cachyos-rt-bore` | BORE+RT | Yes | Realtime + BORE |
| `linux-cachyos-hardened` | BORE | No | No sched_ext |

Companion packages: `scx-scheds`, `scx-tools`, `scx-manager` (GUI)

### CachyOS Repo Setup (on Arch)

Automated:
```bash
curl -o cachyos-repo.tar.xz https://mirror.cachyos.org/cachyos-repo.tar.xz
tar xvf cachyos-repo.tar.xz && cd cachyos-repo
sudo ./cachyos-repo.sh
```

Manual:
```bash
# 1. Import key
sudo pacman-key --recv-keys F3B607488DB35A47 --keyserver keyserver.ubuntu.com
sudo pacman-key --lsign-key F3B607488DB35A47

# 2. Install keyring & mirrorlist packages (get URLs from mirror.cachyos.org)
sudo pacman -U cachyos-keyring-*.pkg.tar.zst cachyos-mirrorlist-*.pkg.tar.zst

# 3. Add to /etc/pacman.conf — pick tier based on CPU:
# x86-64 only:
[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist

# x86-64-v3 (Zen 2+, most modern CPUs):
[cachyos-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
[cachyos-core-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
[cachyos-extra-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist
[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist

# x86-64-v4 (Zen 4/5 only — check with: gcc -march=native -Q --help=target | grep -m1 march):
[cachyos-v4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist
[cachyos-core-v4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist
[cachyos-extra-v4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist
[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist

# 4. Update
sudo pacman -Syu
```

## Xanmod Kernels

### Branches
| Branch | Focus |
|--------|-------|
| MAIN | Latest stable, performance patches |
| EDGE | Very latest (RC candidates) |
| LTS | Long-term support |
| RT | PREEMPT_RT realtime |

### Package names (Debian/Ubuntu from xanmod.org)
- `linux-xanmod` (MAIN)
- `linux-xanmod-edge`
- `linux-xanmod-lts`
- `linux-xanmod-rt`
- `linux-xanmod-x64v2`, `linux-xanmod-x64v3` (optimized instruction set builds)

### Xanmod on Fedora (COPR)
```bash
sudo dnf copr enable rmnscnce/kernel-xanmod
sudo dnf install kernel-xanmod
```

### Xanmod on Debian/Ubuntu
```bash
wget -qO - https://dl.xanmod.org/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/xanmod-archive-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/xanmod-archive-keyring.gpg] http://deb.xanmod.org releases main' | sudo tee /etc/apt/sources.list.d/xanmod-release.list
sudo apt update && sudo apt install linux-xanmod-x64v3
```

## Liquorix (Debian/Ubuntu/Arch)
```bash
# Debian/Ubuntu
curl -s 'https://liquorix.net/install-liquorix.sh' | sudo bash

# Arch (AUR)
paru -S linux-lqx linux-lqx-headers
```

## Fedora Kernels

| Kernel | Source | Notes |
|--------|--------|-------|
| `kernel` | Standard Fedora repo | EEVDF stock |
| `kernel-rt` | Standard Fedora repo | PREEMPT_RT — no COPR needed |
| `kernel-xanmod` | COPR rmnscnce/kernel-xanmod | Xanmod with sched_ext |
| `kernel-ml` | ELRepo (RHEL/CentOS) | Mainline latest |

sched_ext on Fedora:
```bash
sudo dnf copr enable chantra/scx-scheds
sudo dnf install scx-scheds
```

## Ubuntu/Debian Kernels

| Package | Notes |
|---------|-------|
| `linux-image-generic` | Stock |
| `linux-image-lowlatency` | Lower latency, not full RT |
| `linux-generic-hwe-22.04` | HWE track — newer kernel on 22.04 LTS |
| `linux-generic-hwe-24.04` | HWE on 24.04 LTS |

sched_ext: available in Ubuntu 24.04+ universe (`scx-scheds` package).

## openSUSE
- `kernel-default`: standard
- `kernel-preempt`: lower latency (not full RT)
- sched_ext: in Tumbleweed

## NixOS
```nix
boot.kernelPackages = pkgs.linuxPackages_zen;
# or: linuxPackages_cachyos, linuxPackages_xanmod_latest, linuxPackages_lqx, linuxPackages_rt
services.scx.enable = true;
services.scx.scheduler = "scx_lavd";
```
