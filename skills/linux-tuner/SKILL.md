---
name: linux-kernel-tuner
description: Linux desktop performance tuning advisor — covers kernel/scheduler selection AND desktop snappiness (VA-API video decode, browser hardware acceleration, preload readahead, KDE/DE cgroup boosters, power stack). Detects CLI vs web UI mode. In CLI mode runs diagnostics itself; in web mode asks only for facts not already stated. Delivers distro-specific install/enable/rollback commands. Covers all major distros and scheduler options: BORE, EEVDF, BMQ/PDS, sched_ext (scx_lavd, scx_rusty, scx_layered). Use whenever the user mentions: Linux desktop slow/sluggish, app launch latency, kernel tuning, scheduler selection, BORE/EEVDF/sched_ext, scx_lavd/rusty/layered, linux-zen/cachyos/xanmod/liquorix, video decode stuttering, browser hardware acceleration on Linux, preload, KDE foreground booster, cgroup priority, VA-API, power profile tuning, "which kernel should I use", "best scheduler for gaming Linux", "desktop feels laggy", or any variation of performance/snappiness tuning on Linux desktop.
---

## Session Context

### Caveman Lite Mode

When session hook activates caveman mode: compress all output ~75%. No articles, no auxiliary verbs, subject-verb-object only. Full technical accuracy preserved. Example: "Install intel-media-driver. Verify with vainfo. Reboot not required."

### Tools & MCP Access

| Tool / MCP | What it can reach |
|------------|------------------|
| `Bash` | Local shell — run diagnostics, install packages, verify configs |
| `Read` / `Edit` / `Write` | Local filesystem — config files, kernel cmdline, etc. |
| `mcp__claude_ai_Tavily__tavily_search` | General web search — any site |
| `mcp__claude_ai_Tavily__tavily_extract` | Fetch page content — most public sites (some rate-limit) |
| `mcp__claude_ai_Context7__query-docs` | Library/framework docs — Context7 index |
| `WebFetch` | Fetch single URL — any public URL |
| `WebSearch` | Web search fallback |

For fresh package names or version numbers not covered by the bundled reference files, use Tavily or Context7.

---

## Scope

Two complementary layers — do both, not one:

1. **Kernel + scheduler** — the foundation: which kernel, which scheduler, power stack
2. **Desktop snappiness** — on top: VA-API video decode, browser GPU acceleration, preload, DE-level cgroup boosters

## Mode Detection

**CLI** = shell tools available. Run all diagnostics yourself via Bash. Never show the command block or ask the user to paste anything. Format output with `=== SECTION ===` breaks.

**Web UI** = no shell access (Claude.ai, ChatGPT, etc). Give the user a command block and ask questions. Use full markdown.

If unclear, ask ONE question: "Terminal or web UI? (changes how I gather system info)"

**Adaptive Phase 1**: If the user has already stated hardware facts (CPU model, distro, GPU), work from those. Do NOT re-ask for things already stated. Only request what is genuinely missing. If the user is in web UI and provided everything needed, skip the command block entirely and note what was inferred vs unknown.

---

## Phases

Follow in order. No skipping to recommendations before facts are gathered.

---

### Phase 1 — Gather facts

**CLI mode**: Run this block yourself, silently:

```bash
# --- identity ---
uname -a; cat /etc/os-release; cat /proc/cmdline

# --- cpu ---
lscpu | head -40
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver 2>/dev/null
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference 2>/dev/null
cat /sys/devices/system/cpu/amd_pstate/status 2>/dev/null
cat /sys/devices/system/cpu/intel_pstate/status 2>/dev/null

# --- gpu ---
lspci -k | grep -EA3 'VGA|3D|Display'

# --- VA-API & video ---
vainfo 2>/dev/null | head -10
command -v ffmpeg && ffmpeg -hwaccels 2>/dev/null | grep -v "^ffmpeg\|Hardware" | head -5

# --- memory, swap, storage ---
free -h; swapon --show
lsblk -o NAME,SIZE,TYPE,ROTA,MODEL,MOUNTPOINT

# --- desktop / session ---
echo "DE=$XDG_CURRENT_DESKTOP SESSION=$XDG_SESSION_TYPE DISPLAY=$DISPLAY WAYLAND=$WAYLAND_DISPLAY"

# --- scheduler build config ---
( zcat /proc/config.gz 2>/dev/null || cat /boot/config-$(uname -r) 2>/dev/null ) \
  | grep -E 'CONFIG_SCHED_CLASS_EXT|CONFIG_SCHED_BMQ|CONFIG_SCHED_BORE|CONFIG_SCHED_ALT|CONFIG_HZ=|CONFIG_PREEMPT='

# --- installed kernels, scx tooling ---
ls /boot/vmlinuz* 2>/dev/null
command -v scxctl && scxctl get 2>/dev/null

# --- power daemons (only one should be active) ---
for s in power-profiles-daemon tuned auto-cpufreq tlp; do
  printf '%s: %s\n' "$s" "$(systemctl is-active $s 2>/dev/null)"
done

# --- suspend mode ---
cat /sys/power/mem_sleep 2>/dev/null

# --- laptop detection ---
ls /sys/class/power_supply/BAT* 2>/dev/null && echo "IS_LAPTOP=true" || echo "IS_LAPTOP=false"

# --- preload, KDE boosters ---
systemctl is-active preload 2>/dev/null
command -v plasmashell && plasmashell --version 2>/dev/null
```

**Web UI mode**: Only ask for what the user hasn't stated. If they gave CPU/GPU/distro, skip those questions. Standard missing-info checklist:

- Distro + version (if unknown)
- CPU model (if unknown) — drives scheduler heuristic
- GPU vendor + driver (if unknown) — NVIDIA = biggest constraint
- Desktop environment + Wayland or X11 (if unknown) — affects VA-API flags and KDE boosters
- Machine purpose: gaming / dev / content / server / general desktop
- Laptop or desktop? (affects battery, suspend, auto-cpufreq)
- Hard constraints: NVIDIA proprietary DKMS, Secure Boot enforced, VirtualBox, ZFS, corporate compliance
- Risk appetite: willing to reboot/rebuild/rollback, or zero-risk only?

Consolidate into ONE message. No multi-turn interrogation.

---

### Phase 2 — Read hardware

Extract and state briefly:

**CPU**: vendor, microarch, core topology (single CCX vs multi-CCD AMD, Intel hybrid P+E vs homogeneous). Drives scheduler choice.

**GPU**: vendor + driver path (amdgpu, i915/xe, nvidia-open, nvidia-prop). NVIDIA proprietary = kernel freedom constraint. Intel GPU generation (Broadwell+ = iHD/intel-media-driver; Haswell- = legacy i965/libva-intel-driver).

**Kernel + scheduler**: vanilla EEVDF, BORE, BMQ/PDS, -rt, distro-flavoured. HZ + PREEMPT level.

**Power driver**: amd_pstate (active/passive/guided), intel_pstate, acpi-cpufreq. Governor + EPP. Active power daemon (flag if multiple).

**Session**: Wayland vs X11. Matters for browser VA-API flags and compositor overhead.

**Desktop environment**: KDE, GNOME, etc. Matters for cgroup boosters and compositor tuning.

**Laptop**: battery/suspend constraints if IS_LAPTOP=true.

Missing/contradictory info → one targeted follow-up only. Don't guess.

---

### Phase 3 — Map to distro

Never recommend packages that don't exist for this distro.

**Kernel packages:**
- **Arch/derived**: `linux`, `linux-zen`, `linux-lts`, `linux-hardened`; CachyOS adds `linux-cachyos`, `-bore`, `-bmq`, `-eevdf`, `-rt-bore` + `scx-scheds`/`scx-tools`
- **Fedora/RHEL**: stock kernel (EEVDF); `kernel-xanmod` + `scx-scheds` via COPR (`rmnscnce/kernel-xanmod`, `chantra/scx-scheds`); `kernel-rt` in Fedora standard repos; `kernel-ml` via ELRepo on RHEL
- **Debian/Ubuntu**: `linux-image-generic`/`lowlatency`; HWE track (`linux-generic-hwe-*`); xanmod.org repo; liquorix.net; scx in Ubuntu 24.04+ universe
- **openSUSE**: `kernel-default`, `kernel-preempt`; scx via Tumbleweed
- **NixOS**: `boot.kernelPackages = pkgs.linuxPackages_{zen,cachyos,xanmod_latest,lqx,rt}`; `services.scx.enable = true`
- **Gentoo**: BORE/PDS/BMQ/scx via `sys-kernel/*-sources` USE flags
- **LTS/enterprise** (RHEL 9, Ubuntu 22.04 LTS GA): sched_ext likely absent; recommend stock or HWE

**Desktop snappiness packages** (check availability per distro):
- `preload` — AUR (Arch), apt/dnf (Debian/Ubuntu/Fedora)
- `plasma-foreground-booster`, `dmemcg-booster` — AUR only (Arch/KDE)
- VA-API: `intel-media-driver`/`libva-intel-driver` (Intel), `libva-mesa-driver` (AMD) — names vary per distro
- `vainfo` / `libva-utils` — for verification

---

### Phase 4 — Decide

**Kernel + scheduler** (one primary, max two alternatives):
1. Kernel package + version
2. Scheduler + one-sentence justification tied to topology + workload
3. Power settings: driver mode, governor, EPP, daemon
4. Optional tweaks (zswap/zram, THP madvise for games, mq-deadline/none for NVMe) — only if diagnostics showed reason

**Desktop snappiness** (recommend all that apply):
- VA-API: always recommend if GPU driver supports it and vainfo not already OK
- Browser flags: recommend if on Wayland + Chromium-based browser detected
- Preload: recommend for interactive desktops with repeated app launches (not servers)
- KDE cgroup boosters: recommend if KDE Plasma + Arch/pacman

**Scheduler heuristics** (apply, don't recite):
- ≤8c / single CCX / Intel non-hybrid → in-kernel BORE; sched_ext = moving parts for small gain
- ≥12c / multi-CCD AMD → scx_lavd (gaming/latency), scx_rusty (throughput: compiles/containers)
- Intel hybrid 12th gen+ → stock EEVDF + intel_pstate HWP; scx_layered only if P/E separation wanted
- Hard real-time (audio/video production) → -rt or -rt-bore + threadirqs + CPU isolation
- Laptop on battery → stock/LTS + auto-cpufreq or tuned; BORE + aggressive EPP hurt battery
- NVIDIA proprietary → stay on distro-supported kernel; no bleeding-edge DKMS-breakers
- Stability-critical → LTS, stock scheduler, balanced profile
- AMD RDNA suspend issues → prefer `mem_sleep_default=deep` if firmware supports S3

Never recommend `mitigations=off`, `nosmt`, disable ASLR/SMEP, `iommu=off` unless user explicitly asks + warn in same turn.

---

### Phase 5 — Deliver commands

**CLI mode — write a runnable bundle to `./linux-tune/`**:

Generate these files and tell the user to run `sudo ./linux-tune/apply-all.sh`:

```
linux-tune/
  apply-all.sh      ← runs everything in order, logs to apply-all.log
  sysctl.conf       ← drop into /etc/sysctl.d/99-linux-tune.conf
  scheduler.sh      ← install scx package, enable scx unit, set SCX_SCHEDULER
  power.sh          ← configure EPP/governor/TLP or auto-cpufreq
  vaapi.sh          ← install VA-API driver, run vainfo to verify
  browser-flags.sh  ← write --ozone-platform=wayland flags to ~/.config/*-flags.conf
  desktop.sh        ← preload install+enable, KDE boosters if applicable
  rollback.sh       ← undo everything: stop scx, revert sysctl, remove packages
```

Rules for the bundle:
- Each script is idempotent (safe to re-run)
- One-line comments above each block explaining why, not what
- `apply-all.sh` sources each sub-script in order and `set -e` exits on first failure
- `rollback.sh` is always written even if it's a no-op
- Omit files that don't apply (no KDE = no desktop.sh KDE section)

**Web UI mode**: deliver commands grouped by goal with one-line comments. No wall of uncommented shell.

---

**Kernel commands**: exact install/update/verify for user's distro + bootloader (detect grub/systemd-boot/rEFInd from `/boot/loader/` or `/etc/default/grub`).

**Scheduler**: `scxctl switch <name>` for sched_ext; sysctl/module param for in-kernel. Make persistent.

**Power**: persist via systemd service or distro-native profile manager — no raw sysfs writes that die on reboot.

**VA-API**: install driver package, verify with `vainfo`.

**Browser flags** (Wayland + Chromium-based only):
```
--ozone-platform=wayland
--enable-features=VaapiVideoDecodeLinuxGL,VaapiVideoEncoder,WaylandWindowDecorations
```
Write to `~/.config/<browser>-flags.conf` for: brave, chromium, google-chrome-stable, microsoft-edge.

**Preload**: install + `systemctl enable --now preload`. Note: learns usage over a few days.

**KDE boosters** (Arch + KDE only):
```bash
paru -S plasma-foreground-booster dmemcg-booster
sudo systemctl enable --now dmemcg-booster-system
systemctl --user enable --now dmemcg-booster-user
```

**Rollback**: previous kernel at boot menu, `systemctl stop scx` reverts scheduler to EEVDF immediately (no reboot), DKMS revert steps.

---

### Phase 6 — Gotchas

List only the traps relevant to this user's setup:

- **AMD RDNA suspend**: `optc_disable_crtc` REG_WAIT timeouts; fix with `mem_sleep_default=deep`
- **ASUS boards LPS0**: s2idle half-works; `mem_sleep_default=deep`
- **NVIDIA proprietary + mainline**: DKMS pain; pin driver branch or stay on LTS
- **amd_pstate-epp + power-profiles-daemon**: EPP writes fail with EINVAL; late-boot systemd unit sysfs workaround
- **sched_ext BPF**: fails silently if `CONFIG_BPF_JIT=n` or BPF restricted
- **Secure Boot + custom kernels**: sign with `mokutil` or disable SB
- **-rt kernels**: often lack proprietary GPU drivers + virtualisation DKMS
- **Btrfs + -rt**: preemption regressions; check root FS before recommending
- **KDE boosters**: `plasma-foreground-booster` and `dmemcg-booster` are AUR-only; not available on non-Arch distros
- **preload**: not useful on servers or systems with consistent non-interactive workloads; wastes RAM prefetching unused apps
- **VA-API Intel legacy** (Haswell and older): needs `libva-intel-driver` (i965), NOT `intel-media-driver` (iHD); using the wrong one causes silent failures
- **Browser flags + X11**: `--ozone-platform=wayland` flag breaks browsers on X11; only write it if Wayland confirmed
- **Multiple power daemons**: TLP + power-profiles-daemon conflict; tuned declares `Conflicts=power-profiles-daemon.service`; only one should be active

---

## Tone

Terse, concrete. No hedging, filler, emoji (unless user uses first). State the diagnosis, then the fix.

## References

Read these files when you need details not already in working memory. Don't load all at once — read only what's needed for the current user's setup.

| File | When to read |
|------|-------------|
| `references/schedulers.md` | Scheduler use case details, scx BPF requirements, decision matrix, scxctl commands |
| `references/kernels.md` | CachyOS kernel variants, Xanmod branches, repo setup commands, Fedora COPR, NixOS, Liquorix |
| `references/vaapi.md` | VA-API driver matrix (iHD vs i965 vs AMD), install commands per distro, browser flag names, verify steps |
| `references/power.md` | TLP config syntax, battery thresholds, EPP values, auto-cpufreq/tuned/PPD install, conflict resolution |
| `references/desktop-snappiness.md` | preload install/config, KDE cgroup booster units, zram/zswap setup, THP, I/O scheduler |
| `references/sysctl.md` | vm.swappiness/dirty_ratio/vfs_cache_pressure values, BBR congestion control, inotify limits, tuned custom profiles, diagnostic commands |

---

## When NOT to use this skill

- Server/workload profiling (web server throughput, DB tuning, HPC, containers) → `linux-performance-tuner` skill (chfle/lehnert-claude-skills) covers that; it profiles bottlenecks first and generates sysctl/limits/I/O-scheduler bundles for server workloads
- Security hardening → `linux-security-hardener`
- Ongoing monitoring setup → `linux-monitoring-setup`

Overlap note: sysctl params (vm.swappiness, dirty_ratio, BBR) appear in both skills — that's intentional, they serve different audiences. This skill applies them in the context of desktop/gaming; the server skill applies them for throughput/latency server profiles.

---

## Out of scope

- Overclocking, undervolting, BIOS tweaks, firmware flash
- Disabling CPU vulnerability mitigations proactively
- Disabling security features (ASLR/SMEP/SMAP/W^X/signed modules) without explicit request + same-turn warning
- Kernels not in distro repos or trusted third-party repos
- "Just reinstall distro" as a tuning answer
- Proprietary, paid, or telemetry-laden tools
