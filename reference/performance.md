# Performance — GameMode, MangoHud, CPU Power, Tuning

## GameMode

Daemon that applies system optimizations when a game starts. Games request it via D-Bus or `libgamemodeauto.so` preload.

**What it actually does:**
- Switches CPU governor to `performance` (requires user in `gamemode` group)
- Optionally renices game process (configure in `/etc/gamemode.ini`)
- Optionally overclocks GPU (AMD: set `amd_performance_level` in `/etc/gamemode.ini` — requires `amdgpu.ppfeaturemask` kernel param, see `gpu.md`)

**Steam integration:**
```bash
gamemoderun %command%          # activate per-game
gamemoderun mangohud %command% # combined with MangoHud overlay
gamemoderun steam              # activate for whole Steam session
```

**Verify:**
```bash
gamemoded -t    # test configuration
gamemoded -s    # check if running
```

**Prerequisites:** User must be in `gamemode` group. For 32-bit games: install `lib32-gamemode`. GPU overclocking config must be in `/etc/gamemode.ini` (not user config — security restriction).

**Config priority:** `$PWD/gamemode.ini` → `~/.config/gamemode.ini` → `/etc/gamemode.ini` → `/usr/share/gamemode/gamemode.ini`

## MangoHud

In-game overlay showing FPS, GPU/CPU usage, temps, frame timing. Vulkan + OpenGL both supported.

**Install:** `mangohud` + `lib32-mangohud` (for 32-bit games). GUI config: `goverlay` or `mangojuice`.

```bash
mangohud %command%                     # enable for one game
MANGOHUD=1 %command%                   # alternative
MANGOHUD_DLSYM=0 %command%            # OpenGL apps that override LD_PRELOAD (prevents double-inject)
mangohud gamemoderun %command%         # combined with GameMode
mangohud steam                         # auto-enables for all games launched from this Steam instance
```

**Config file priority** (all read & merged):
1. `$XDG_CONFIG_HOME/MangoHud/MangoHud.conf`
2. `$XDG_CONFIG_HOME/MangoHud/APPLICATION-NAME.conf` (per-app, case-sensitive)
3. `$XDG_CONFIG_HOME/MangoHud/wine-APPLICATION-NAME.conf` (Wine apps, no `.exe` extension)
4. `./MangoHud.conf`
5. `$MANGOHUD_CONFIGFILE` (env var override)

**Default keyboard shortcuts:**
| Shortcut | Action |
|----------|--------|
| `Shift_R+F12` | Toggle overlay on/off |
| `Shift_R+F11` | Move overlay position |
| `Shift_R+F10` | Cycle preset |
| `Shift_L+F1` | Toggle FPS limit |
| `Shift_L+F2` | Start/stop metric logging |
| `Shift_L+F4` | Reload config |
| `Shift_L+F3` | Upload log |
| `Shift_R+F9` | Reset FPS metrics |

**Test:** `mangohud glxgears` (OpenGL) or `mangohud vkcube` (Vulkan)

**OpenGL apps that break:** Some native Linux games override `LD_PRELOAD` — MangoHud won't load. Workaround: edit the game's start script and set `LD_PRELOAD=/usr/lib/mangohud/`.

**Inside gamescope:** Use `--mangoapp` flag on the gamescope invocation instead of standard MangoHud — MangoHud inside a gamescope session causes swapchain errors. FSR/HDR status indicators only work with `--mangoapp`.

## Gamescope Performance Flags

```bash
gamescope -r 60               # framerate cap
-F fsr                        # AMD FSR upscaling (render lower, display higher)
-F nis                        # NVIDIA NIS upscaling
--adaptive-sync               # enable VRR/FreeSync
--hdr-enabled                 # HDR (embedded KMS mode only; see display.md for VRR+HDR caveats)
```

## Scheduler Tuning (CachyOS/Nobara specific)

- **CachyOS**: LAVD scheduler default on Handheld Edition (latency/power optimized)
- **Nobara**: `falcond.service` auto-selects SCX scheduler (`bpfland`/`lavd`/`rusty`/`flash`) per game; manages AMD 3D VCache mode

## CPU Power Management

CPU governor choice significantly impacts gaming performance. Default is `schedutil` (kernel-managed); for gaming, `performance` is highest throughput.

### Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `cpupower` | Set governor + frequency limits | `cpupower.service` applies at boot |
| `power-profiles-daemon` | `balanced` / `performance` / `power-saver` profiles | KDE + GNOME have native GUI; `powerprofilesctl` CLI |
| `tuned` | Advanced adaptive tuning (Fedora-native but works everywhere) | Conflicts with power-profiles-daemon; use one |
| `auto-cpufreq` | Automatic laptop optimizer (battery state + load aware) | Best for laptops |
| `thermald` | Intel CPU thermal daemon; unlocks performance on Tiger Lake laptops | Intel-only |

```bash
# cpupower: set governor
cpupower frequency-set -g performance   # max performance
cpupower frequency-info                 # show current governor + limits

# power-profiles-daemon
powerprofilesctl list
powerprofilesctl set performance

# Permanent via cpupower.service
# Edit /etc/default/cpupower-service.conf: governor='performance'
# systemctl enable cpupower.service

# turbostat: Intel/AMD frequency + power live view
sudo turbostat --quiet --interval 1 --show CPU,Busy%,Avg_MHz,Bzy_MHz,PkgWatt
```

**GameMode automatically switches to `performance` governor** when a game starts — no manual config needed if using GameMode. User must be in `gamemode` group.

**amd_pstate driver** (AMD Zen3+ / Ryzen 6000+): replaces `acpi_cpufreq`; supports hardware-guided frequency scaling. Enable with `amd_pstate=active` kernel parameter for best efficiency.

## CPU / Memory Tuning (advanced, 🔴 Deep)

**Threading sync generations** (Wine/Proton):
- `esync` (oldest) — uses `eventfd`; raises `nofile` ulimit requirement
- `fsync` / `futex2` — kernel 5.16+; most Proton versions default
- `ntsync` — kernel 6.14+, closest to Windows behavior; CachyOS enables by default. Disable with `PROTON_USE_NTSYNC=0` if broken

**AMD Zen3/Zen4/Zen5 chiplet isolation** — each 8-core CCD has its own 32MB L3 cache; pinning game to one CCD reduces cache contention when streaming simultaneously:
```bash
# pin game to cores 0-7 (first CCD)
taskset -c 0-7 gamemoderun %command%
# or via cpuset (persistent)
```

**x2APIC on Ryzen** — improves interrupt handling; enable in BIOS, then add `x2apic_phys` kernel parameter.

**Wayland-native Wine** — avoids XWayland overhead on pure Wayland setups:
```bash
PROTON_ENABLE_WAYLAND=1 %command%   # Proton (GE / cachyos)
DISPLAY="" wine executable.exe      # bare Wine with Wayland driver
```
