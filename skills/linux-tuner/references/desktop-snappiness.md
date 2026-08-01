# Desktop Snappiness Reference

## preload

Adaptive readahead daemon. Learns app usage patterns via Markov chains, prefetches binaries and shared libs into page cache before user opens them. Reduces perceived app launch latency.

**Good for**: Interactive desktops, users with consistent app patterns, systems with 8GB+ RAM.
**Not useful for**: Servers, systems with inconsistent/non-interactive workloads (wastes RAM prefetching unused apps), systems with <4GB RAM.

### Install

**Arch (AUR)**:
```bash
paru -S preload
sudo systemctl enable --now preload
```

**Debian/Ubuntu**:
```bash
sudo apt install preload
sudo systemctl enable --now preload
```

**Fedora**:
```bash
sudo dnf install preload
sudo systemctl enable --now preload
```

### Config

`/etc/preload.conf` — defaults are fine; rarely needs tuning.

Key options:
```ini
# Minimum RAM MB before preload backs off aggressively
memfree=50

# How much to log (0=quiet, 9=debug)
loglevel=1
```

Preload learns usage over a few days — don't expect instant results.

### Verify
```bash
systemctl status preload
# Check preload is reading/caching:
journalctl -u preload -n 20
```

---

## KDE Cgroup Boosters

**Available**: AUR only. Arch + KDE Plasma exclusively. Not available on Fedora, Ubuntu, or other distros.

### What they do

- `plasma-foreground-booster`: Raises CPU priority (cgroup weight) of the active foreground window's process tree. Makes focused apps feel more responsive.
- `dmemcg-booster`: Memory cgroup booster — gives foreground apps priority in kernel memory reclaim decisions.

### Install

```bash
paru -S plasma-foreground-booster dmemcg-booster
```

### Enable

```bash
# System-level memory cgroup booster (requires sudo)
sudo systemctl enable --now dmemcg-booster-system

# User-level cgroup booster
systemctl --user enable --now dmemcg-booster-user
```

### Notes
- KDE Plasma 5.27+ or Plasma 6 recommended
- Requires systemd cgroup v2 (cgroup2) — standard on modern distros
- No config needed; works automatically after enabling units
- Verify: `systemctl status dmemcg-booster-system` and `systemctl --user status dmemcg-booster-user`

---

## zram / zswap

For RAM-constrained systems (< 16GB):

**zram** (compressed swap in RAM, faster than disk swap):
```bash
# Arch
sudo pacman -S zram-generator
# Create /etc/systemd/zram-generator.conf:
[zram0]
zram-size = ram / 2
compression-algorithm = zstd

# Ubuntu/Fedora — often enabled by default in newer releases
# Check: ls /dev/zram*
```

**zswap** (compressed swap cache in front of disk swap):
```bash
# Add to kernel cmdline: zswap.enabled=1 zswap.compressor=zstd zswap.zpool=z3fold
# Check if active: cat /sys/module/zswap/parameters/enabled
```

---

## Transparent Hugepages (THP)

For gaming: set to `madvise` (games can request THP explicitly, normal apps unaffected):
```bash
echo madvise | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
# Persist via tmpfiles.d or kernel cmdline: transparent_hugepage=madvise
```

Avoid `always` on desktop — causes latency spikes for small-allocation workloads.

---

## I/O Scheduler

For NVMe SSDs: use `none` (drive's own queue handles scheduling):
```bash
echo none | sudo tee /sys/block/nvme0n1/queue/scheduler
```

For SATA SSD: `mq-deadline` is good default.

For HDD: `bfq` or `mq-deadline`.

Make persistent via udev rule `/etc/udev/rules.d/60-ioscheduler.rules`:
```
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
ACTION=="add|change", KERNEL=="sd[a-z]|mmcblk[0-9]*", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="mq-deadline"
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="bfq"
```
