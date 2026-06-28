# Sysctl Tuning Reference

Sources: linuxnest.com sysadmin guide, RHEL 7 Performance Tuning Guide (concepts apply to modern kernels)

## Persist changes

Temporary (lost on reboot):
```bash
sudo sysctl -w vm.swappiness=10
```

Permanent — drop file in `/etc/sysctl.d/`:
```bash
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.d/99-performance.conf
sudo sysctl -p /etc/sysctl.d/99-performance.conf
```

---

## Virtual Memory

| Parameter | Desktop default | Gaming/interactive | Server throughput | Notes |
|-----------|----------------|-------------------|------------------|-------|
| `vm.swappiness` | 60 | 10 | 10–30 | Lower = prefer RAM over swap; set to 10 on desktops with enough RAM |
| `vm.dirty_ratio` | 20 | 30 | 40–60 | Max % RAM with dirty pages before writeback blocks; higher = more write buffering |
| `vm.dirty_background_ratio` | 10 | 10 | 10–20 | % RAM with dirty pages before background writeback starts |
| `vm.vfs_cache_pressure` | 100 | 50 | 50 | Lower = keep directory/inode caches longer; better for desktop with many files |

```bash
# Desktop/gaming tuning block
sudo tee /etc/sysctl.d/99-desktop-perf.conf <<'EOF'
vm.swappiness=10
vm.dirty_ratio=30
vm.dirty_background_ratio=10
vm.vfs_cache_pressure=50
EOF
sudo sysctl -p /etc/sysctl.d/99-desktop-perf.conf
```

## Transparent Hugepages via sysctl

THP is kernel-controlled, not sysctl — set via sysfs (see desktop-snappiness.md).

Disable NUMA balancing (can hurt latency on gaming/single-socket):
```bash
echo 0 | sudo tee /proc/sys/kernel/numa_balancing
# or: kernel.numa_balancing=0 in sysctl.d
```

## File System / inotify

```bash
# inotify watches — needed for IDEs, file sync tools, many file watchers
fs.inotify.max_user_watches=524288

# Max open file handles (servers / high-concurrency)
fs.file-max=2097152
```

---

## Network Stack

For desktop gaming and general use — conservative tuning:
```bash
# TCP BBR congestion control (better latency/throughput on variable networks)
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
```

Check if BBR is available:
```bash
sysctl net.ipv4.tcp_available_congestion_control | grep bbr
```

For high-bandwidth workloads (file servers, video streaming):
```bash
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
```

---

## tuned Custom Profiles (RHEL/Fedora/openSUSE)

Extend a base profile without modifying it:
```
/etc/tuned/my-desktop/tuned.conf:
[main]
include=balanced

[sysctl]
vm.swappiness=10
vm.vfs_cache_pressure=50
```

Activate: `sudo tuned-adm profile my-desktop`

### Relevant tuned profiles for desktop

| Profile | Use case |
|---------|----------|
| `balanced` | Default; good starting point for laptops |
| `desktop` | Explicitly for interactive desktop responsiveness |
| `latency-performance` | Low latency, disables power savings, locks low C-states |
| `throughput-performance` | Max I/O and network throughput (server) |
| `network-latency` | Based on latency-performance + disables THP + NUMA balancing |
| `realtime` | Full RT tuning for audio/video production |
| `powersave` | Max power saving |

Custom profiles in `/etc/tuned/` survive tuned package updates.

---

## CPU Isolation (RT audio / low-latency workloads)

Remove CPUs from the general scheduler so RT processes get exclusive access. Kernel cmdline params:

```
isolcpus=2,3,4,5 nohz_full=2-5 rcu_nocbs=2-5
```

Apply (GRUB):
```bash
# 1. Edit /etc/default/grub — add to GRUB_CMDLINE_LINUX
sudo nano /etc/default/grub

# 2. Update bootloader + reboot
sudo update-grub && sudo reboot

# 3. Verify after reboot
cat /proc/cmdline | grep isolcpus
```

Apply (systemd-boot):
```bash
# Edit /boot/loader/entries/*.conf — append to options line
sudo nano /boot/loader/entries/arch.conf
# Add: isolcpus=2,3 nohz_full=2-3 rcu_nocbs=2-3
```

Then pin RT process to isolated cores:
```bash
taskset -c 2,3 jackd ...
# or: chrt -f 80 taskset -c 2,3 <command>
```

Pair with: `-rt` or `-rt-bore` kernel + `threadirqs` param + `CPU_BOOST_ON_AC=0` in TLP (reduces frequency variance).

---

## Useful Diagnostics

```bash
# Overall system load
uptime

# CPU, memory, processes
htop

# Memory and swap stats every 2s
vmstat 2

# I/O stats
iostat -xz 2

# Network connections
ss -tuln

# Per-process I/O
iotop

# NUMA topology
numactl --hardware

# CPU frequency and power states (Intel)
turbostat --Summary --quiet

# Performance profiling — flamegraph
perf record -F 99 -a -g -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
# Open flame.svg in browser to see hotspots

# Quick per-process CPU
perf top
perf stat <command>
```
