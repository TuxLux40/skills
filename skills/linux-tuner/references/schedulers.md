# Scheduler Reference

## sched_ext BPF Requirements

Kernel must be built with:
```
CONFIG_BPF=y
CONFIG_BPF_JIT=y
CONFIG_DEBUG_INFO_BTF=y
CONFIG_SCHED_CLASS_EXT=y  # upstream since kernel 6.12
```

Check: `( zcat /proc/config.gz || cat /boot/config-$(uname -r) ) | grep CONFIG_SCHED_CLASS_EXT`

Fails silently if `CONFIG_BPF_JIT=n` or BPF restricted by sysctl.

## scx Scheduler Use Cases

### scx_lavd
- **Best for**: Gaming, interactive desktop, high-interactivity apps
- **Algorithm**: LAVD (Latency-criticality Aware Virtual Deadline) — measures how latency-critical each task is, uses that in scheduling decisions
- **Topology**: Creates separate scheduling domain per-LLC, per-core type (P/E on Intel, big/LITTLE on ARM), per-NUMA domain
- **Targets**: Primarily single CCX / single-socket systems. Multi-CCX AMD works but scx_rusty may be better there
- **Commands**: `scxctl switch scx_lavd`, or `scx_lavd --performance` for gaming profile

### scx_rusty
- **Best for**: Throughput workloads — compiles, containers, background batch jobs
- **Topology**: Creates scheduling domain per-LLC. Performant on multi-CCX where all LLCs share same socket. Multi-socket machines may be sub-optimal (NUMA unawareness)
- **Note**: Known infeasible-weights issue — very high weight task can cause scheduler to leave cores idle. Affects CFS too; not specific to scx_rusty
- **Commands**: `scxctl switch scx_rusty`

### scx_layered
- **Best for**: Mixed workloads where you want explicit control over which CPUs certain tasks run on — e.g., isolating latency-sensitive tasks to P-cores on Intel hybrid
- **Config**: JSON config file defines layers. Each layer can pin tasks by cgroup, command, or nice value. `perf` field (0-1024) controls frequency scaling (requires `schedutil` governor). `slice_us` tunes timeslice per layer
- **Use case**: Intel 12th gen+ with P+E cores; or isolating audio/RT tasks to specific core set
- **Commands**: `scxctl switch scx_layered --config /path/to/layers.json`

### scx_bpfland
- **Best for**: Interactive workloads running alongside CPU-intensive background tasks — gaming, live streaming, multimedia, real-time audio/video encoding
- **Algorithm**: Tasks that are more interactive (sleep more, use CPU less = smaller runtime) get higher priority in queue. Tasks get time-slice budget: dispatched with remaining unused portion of previous slice (latency-sensitive tasks can exceed slice for short CPU bursts without interruption)
- **Production ready**: Yes
- **Commands**: `scxctl switch scx_bpfland`

## In-Kernel Schedulers

### BORE (Burst-Oriented Response Enhancer)
- Patch on top of EEVDF. Adds burstiness score to reward interactive tasks.
- Available: CachyOS (`linux-cachyos-bore`), Xanmod, Liquorix. No sched_ext required.
- Best for: ≤8c single-CCX systems; gaming on kernels without sched_ext support

### EEVDF (Earliest Eligible Virtual Deadline First)
- Stock upstream scheduler since kernel 6.6. Replaced CFS.
- Available everywhere.

### BMQ/PDS (Project C)
- Available in CachyOS (`linux-cachyos-bmq`) and some Xanmod builds
- `linux-cachyos-bmq`: does NOT support sched_ext (incompatible)

### -rt / PREEMPT_RT
- Hard realtime: eliminates most non-preemptible sections
- Required for pro audio, video production with tight latency requirements
- Add `threadirqs` kernel param alongside for extra latency reduction
- Often incompatible with proprietary NVIDIA DKMS drivers

## scxctl Commands

```bash
scxctl get          # show active scheduler
scxctl list         # list available schedulers
scxctl switch scx_lavd   # switch (immediate, no reboot)
systemctl stop scx  # revert to EEVDF (immediate)
```

Make persistent: `systemctl enable scx` + set `SCX_SCHEDULER=scx_lavd` in `/etc/default/scx`

## Decision Matrix

| Scenario | Scheduler |
|----------|-----------|
| Single CCX (≤8c), general desktop | BORE (in-kernel) |
| Multi-CCD AMD (≥12c), gaming | scx_lavd |
| Multi-CCD AMD, compiles/containers | scx_rusty |
| Intel hybrid 12th gen+, mixed workloads | EEVDF stock or scx_layered |
| Pro audio / RT production | -rt-bore or -rt + threadirqs |
| NVIDIA proprietary, stability-first | BORE or stock EEVDF |
| Laptop on battery, low power | Stock/LTS + EEVDF |
