---
name: steam-debugger
description: Use when troubleshooting Steam on Linux gaming distros (SteamOS, Bazzite, ChimeraOS, CachyOS, Nobara), gamescope session issues, Steam Linux Runtime problems, Proton failures, services not starting in gaming mode, DRM/KMS device conflicts, environment variable pollution, no game audio, AMD GPU hangs, HDR/VRR problems, or any issue where behavior differs between gaming mode and desktop mode. Also use when wiring services to the gamescope session or diagnosing why a game behaves differently under gamescope vs desktop.
---

# Steam Debugger — Linux Gaming Session Reference

Self-contained troubleshooting skill for Steam on Linux. Knowledge is split across reference files — load only what the symptom routes to.

## Output Style (caveman lite)

Respond terse. Drop filler words (just/really/basically/actually), pleasantries (sure/certainly/happy to), and hedging. Keep full sentences and articles where dropping them would hurt clarity — this is *lite*, not telegraph style. All technical substance stays: exact package names, exact error strings, exact paths. Code blocks and commands always written normally.

Pattern: `[diagnosis]. [reason]. [fix or next step].`

- Not: "Sure! The issue you're experiencing is most likely caused by the fact that the service isn't wired to the gaming session target."
- Yes: "Service skips gaming mode. It's wired to `graphical-session.target`, which gamescope never activates. Fix: add `WantedBy=gamescope-session.target`."

**Drop terse mode entirely for:** security warnings, irreversible-action confirmations (🔴 Deep tier fixes), and any explanation aimed at a layperson who asked what a command does. Clarity for non-experts beats brevity — that is the whole point of the triage protocol below.

## File Map

| File | Contents |
|------|----------|
| `reference/session-architecture.md` | Gamescope modes, distro session stacks, systemd targets, Steam Linux Runtime, environment variables, the 7 common failure patterns |
| `reference/steam-client.md` | Steam installation, directory layout, launch options format, client/runtime error tables, NTFS, Remote Play, debugging tools |
| `reference/gpu.md` | AMD driver stack, kernel module params, power management sysfs, known hardware issues, RADV, hybrid graphics (PRIME), DKMS |
| `reference/gpu-nvidia.md` | NVIDIA driver choice (nvidia/nvidia-open/NVK), version-match rule, KMS, Secure Boot, suspend VRAM, Wayland/gamescope quirks, Xid errors |
| `reference/input.md` | Controller setup, udev rules, per-pad drivers (xpadneo/xone/hid_playstation), double-input bug, Steam Input, SDL mappings |
| `reference/audio.md` | PipeWire architecture, config locations, failure table, ALSA troubleshooting |
| `reference/wine-proton.md` | Proton troubleshooting, Wine prefixes, winetricks, DLL overrides, Wine builds/managers, anti-cheat compatibility, cloud gaming |
| `reference/performance.md` | GameMode, MangoHud, CPU power management, scheduler tuning, advanced CPU/memory tuning |
| `reference/display.md` | Gamescope-specific troubleshooting, HDR, hardware raytracing, VRR, Wayland color management |
| `reference/steam-deck.md` | Deck hardware IDs, firmware shortcuts, OLED audio, controller modes |
| `reference/tribal.md` | 🟣 Anecdotal community fixes with provenance — last resort after documented fixes fail |
| `reference/sources.md` | All source URLs (Arch Wiki, Valve, distro docs) with scraper-blocked-site warnings |
| `scripts/` | Read-only diagnostic evidence collectors (see Diagnostic Scripts below) |

## Triage Protocol (Read First)

Users reporting gaming issues are usually **not Linux experts**. Before suggesting any fix, gather context with these intake questions. Do not assume — ask.

### Step 1: Establish context (ask all that are unknown)

| Question | Why it matters |
|----------|---------------|
| "Which distro are you on?" (SteamOS/Bazzite/CachyOS/ChimeraOS/Nobara/other?) | Session stack, available tools, and fix paths differ per distro |
| "Which GPU?" (AMD/NVIDIA/Intel, model if possible) | Driver, Vulkan stack, and known bugs are GPU-specific |
| "Does this happen in gaming mode, desktop mode, or both?" | Determines whether the cause is gamescope-session vs desktop session |
| "What exactly happens?" (error message, freeze, black screen, no audio, crash?) | Routes to the right failure pattern |
| "Did anything change recently?" (update, new plugin, config edit, hardware change?) | Most regressions have a proximate cause |
| "Does this happen with all games or one specific game?" | Isolates game-specific vs system-wide issues |

### Step 2: Route by symptom

| Symptom | Load |
|---------|------|
| Gaming mode won't start / boot hangs / loops | `session-architecture.md` → DRM master conflict |
| Works on desktop, broken in gaming mode | `session-architecture.md` → Session target mismatch / WAYLAND_DISPLAY pollution |
| Services/plugins not running in gaming mode | `session-architecture.md` → systemd session wiring |
| Game crashes / won't launch | `wine-proton.md` → Proton troubleshooting |
| Game launches but no audio | `audio.md` |
| No audio in specific game (Project Zomboid, FMOD games) | `audio.md` → FMOD fix (install pipewire-alsa) |
| Audio crackling on Wine / Steam Deck | `audio.md` → min-quantum config |
| Stuttering / bad performance | `performance.md` |
| CPU stuck at low clocks during gaming | `performance.md` → CPU Power Management |
| Game not available on Linux (anti-cheat) | `wine-proton.md` → Anti-Cheat |
| Game needs anti-cheat that blocks Linux (Fortnite, Valorant) | `wine-proton.md` → Cloud Gaming |
| AMD GPU artifacts / hang / freeze | `gpu.md` → Known AMD Hardware Issues |
| amdgpu module not loading / wrong driver on old AMD card | `gpu.md` → Required packages |
| Laptop: game won't use discrete GPU | `gpu.md` → Hybrid Graphics |
| Works with one Proton version, not another | `session-architecture.md` → Steam Linux Runtime |
| HDR not working / washed out / missing toggle | `display.md` → HDR |
| Raytracing not rendering / no RT option | `display.md` → Hardware Raytracing |
| Cursor not captured / fullscreen perf bug / mangohud swapchain errors | `display.md` → Gamescope-Specific Troubleshooting |
| Steam client errors (GLIBCXX, missing libs, store won't load, slow downloads) | `steam-client.md` |
| Game on NTFS won't start | `steam-client.md` → NTFS / filesystem |
| Wine game crashes / won't start (non-Steam) | `wine-proton.md` → Wine section |
| Game on GOG/Epic/itch.io (not in Steam) | `wine-proton.md` → Wine managers |
| Steam Deck hardware question (firmware, OLED audio, controller) | `steam-deck.md` |
| Controller not detected / wrong buttons / double input | `input.md` |
| NVIDIA: driver won't load, black screen, post-suspend crashes, version mismatch | `gpu-nvidia.md` |
| Flatpak Steam: drives invisible, MangoHud/protontricks broken, controller blocked | `steam-client.md` → Flatpak Steam |
| In-game launcher broken (EA App, Ubisoft Connect, Rockstar) | `wine-proton.md` → In-Game Launchers |
| Stuck "Processing Vulkan shaders" / shader stutter | `performance.md` → Shader Pre-Compilation |
| Game killed silently mid-session / OOM | `performance.md` → Memory Pressure |
| Recording or streaming game capture | `performance.md` → Recording |
| Documented fixes exhausted, symptom persists | `tribal.md` (🟣 disclose provenance) |

### Step 3: Match fix to user comfort level

Before running any fix, state which tier it is and what it does. For **Deep/Risky** fixes, explain the risk and ask for confirmation. Never assume a layperson knows what `loginctl`, `modprobe`, or `sysfs` are — explain briefly before using them.

**Escalation order:** ✅ Official → ⚠️ Community-documented → 🟣 Tribal (`reference/tribal.md`) → 🔴 Deep. Don't skip ahead; exhaust the safer tier for the symptom first.

## Fix Tiers

### ✅ Official / Fully supported
Actions Valve and distro maintainers explicitly document and expect:
- Steam launch options (`PROTON_*`, `LD_PRELOAD=""`, `STEAM_COMPAT_DATA_PATH`, `gamescope -- %COMMAND%`)
- `steamos-session-select gamescope|plasma` (SteamOS/Bazzite session switching)
- `ujust` commands on Bazzite
- systemd user service drop-ins for your own services (not editing shipped units)
- `protontricks <appid> <verb>` for per-prefix Winetricks installs
- `protontricks-launch` for running binaries inside a prefix
- ProtonDB-listed fixes (launch options, env vars)
- Decky Loader plugins (official plugin store)

### ⚠️ Supported-unofficial / Community-documented
Widely used, generally safe, but not explicitly documented by Valve:
- GE-Proton (Proton-GE) as a compatibility tool override
- MangoHud, GameMode, Feral GameMode integration
- `mangohud %COMMAND%` in launch options
- Per-service `WantedBy=gamescope-session.target` drop-ins for third-party user services
- `steam-native` / `STEAM_RUNTIME=0` for debugging
- Editing `config.vdf` or `shortcuts.vdf` with Steam closed (well-understood format)
- `MESA_VK_DEVICE_SELECT` for GPU selection
- `SteamInput=2` in `localconfig.vdf` to disable Steam Input per-game

### 🟣 Tribal / anecdotal (last resort)
Fixes from community discussion (Discord, forum threads, Reddit comments) that worked for *someone* but have no official documentation. Stored in `reference/tribal.md` with provenance. **Only reach for these after ✅ and ⚠️ fixes for the symptom have been tried and failed.** Always tell the user the fix is anecdotal, cite its provenance, and prefer reversible variants.

### 🔴 Deep / Risky
Bypasses normal update paths, may break on package updates, or has system-wide side effects:
- Editing shipped gamescope-session unit files directly (use drop-ins instead)
- `loginctl enable-linger` / `loginctl disable-linger` (affects all user services at boot)
- Patching plugin-manager plugin files (reverted on plugin updates)
- `STEAM_RUNTIME=0` for daily use (widespread compat breakage)
- Disabling `VkLayer_FROG_gamescope_wsi` (`DISABLE_GAMESCOPE_WSI=1`) — disables VRR/HDR/scaling handoff inside gamescope; band-aid only
- Kernel parameters (`nvidia-drm.modeset=1`, `AMD_PRIVATE_COLOR` for VRR+HDR)
- Editing `/etc/profile.d/` scripts that affect the login environment (daemon guard vars)
- Rebuilding gamescope or Proton from source against system headers

## Log Locations

| What | Path / Command |
|------|---------------|
| Steam stdout/stderr | `/tmp/dumps/USER_stdout.txt` (always written, no terminal needed) |
| Gamescope session | `journalctl --user -u gamescope-session.service -b 0` |
| Gamescope compositor | Stderr captured by session service; in journal above |
| Proton/game | `~/.steam/root/steamapps/compatdata/<appid>/` + `steam-<appid>.log` |
| Current boot (all) | `journalctl -b 0` |
| Previous boot | `journalctl -b -1` |
| Decky Loader | `journalctl -u plugin_loader.service -b 0` |

## Diagnostic Scripts

Read-only evidence collectors in `scripts/`. Run these instead of issuing the equivalent commands one by one — each produces a structured snapshot and degrades gracefully when tools are missing.

| Script | Collects |
|--------|----------|
| `scripts/diagnose-session.sh` | logind sessions, linger state, DRM device holders, gamescope target/service state, journal greps for KMS/DRM failures, runtime env vars, failed user units |
| `scripts/gpu-info.sh` | PCI GPU list + kernel driver in use, Vulkan devices, AMD sysfs power state/clocks/VRAM/temps, kernel GPU error messages |
| `scripts/audio-snapshot.sh` | Audio server identity, PipeWire/WirePlumber service state, sinks/sources, default devices, ALSA card list, 32-bit/ALSA-bridge package presence |

All scripts are POSIX sh, mutate nothing, and print `(skipped: <tool> not found)` for unavailable tools. Some checks need root (`fuser` on `/dev/dri`, `dmesg` on locked-down kernels) — scripts note when output is incomplete for that reason.

Manual one-liners (when scripts unavailable):
```bash
loginctl list-sessions                    # who is on which seat, what class
loginctl show-user $USER -p Linger        # linger enabled? (can cause seatless sessions)
sudo fuser -v /dev/dri/card*              # who holds the GPU right now
systemctl --user list-dependencies gamescope-session.target --no-pager
journalctl -b 0 | grep -iE 'Started Gamescope|Could not open KMS|Device or resource busy|Failed to create backend|gamescope.*segfault'
env | grep -E 'STEAM|LD_PRELOAD|LD_LIBRARY|PROTON|PRESSURE'
cat ~/.steam/root/steamapps/compatdata/<appid>/version   # which Proton last ran this prefix
```

## Mental Model: All Hardware Conflicts Share One Pattern

> **Device → single-owner privilege → arbiter → unexpected second claimant**

| Device | Privilege | Arbiter | Typical second claimant |
|--------|-----------|---------|------------------------|
| `/dev/dri/card*` | DRM master | logind | Seatless lingering session, another compositor |
| USB HID endpoint | First grabber | Kernel HID subsystem | Two instances of same daemon |
| Vulkan device | First acquirer | Driver | Two compositors both requesting exclusive access |

When something "doesn't work," ask: **who is holding the device, and what is telling the second claimant no?**
Tools: `sudo fuser -v <device>`, `loginctl list-sessions`, journal grep for `busy|denied|TakeDevice`.
