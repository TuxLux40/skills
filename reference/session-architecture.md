# Session Architecture — Gamescope, systemd, Steam Linux Runtime

## Gamescope: What It Is

**Micro-compositor** (formerly steamcompmgr). Runs games in isolated Xwayland sessions, manages frame presentation via DRM/KMS.

### Two Operation Modes

| Mode | Used When | DRM Behavior |
|------|-----------|-------------|
| **Nested** | Running on top of existing X11/Wayland desktop | Renders into a window on the host compositor |
| **Embedded** (standalone) | Gaming distros, SteamOS, Big Picture boot | Takes **direct DRM/KMS ownership** of `/dev/dri/card*`; no other compositor running |

Gaming distros always use **embedded mode**. This is why gamescope needs to be the *only* process with DRM master — and why seatless processes, linger sessions, or leaked `WAYLAND_DISPLAY` break it.

### Frame Pipeline (embedded mode)
1. Game renders → Xwayland (no copy)
2. Gamescope flips frame directly via DRM/KMS (no copy)
3. GPU composition fallback (overlays/scaling) → async Vulkan compute

## Distro Session Stacks

| Distro | Base | Session Package | Session Switcher | Root FS |
|--------|------|----------------|-----------------|---------|
| **SteamOS 3** | Arch-based | `gamescope-session` (Valve upstream) | `steamos-session-select` | Read-only |
| **Bazzite** | Fedora Atomic (OCI image) | `gamescope-session` (Valve upstream) | `steamos-session-select` | Immutable image |
| **ChimeraOS** | Arch (read-only root) | `gamescope-session-plus` + `gamescope-session-steam` | — | Btrfs read-only root |
| **CachyOS** | Arch (mutable) | `gamescope-session-cachyos` (Valve fork) | `plasma-login-manager` | Btrfs mutable |
| **Nobara** | Fedora (mutable RPM) | `gamescope-session-plus` + `gamescope-session-steam` + `gamescope-session-common` | Session shortcut | RPM mutable |

### Unique per-distro components

- **Bazzite**: `ujust setup-decky` (Decky install); `ujust` toolset; Handheld Daemon (`hhd`) for non-Deck handhelds; `-deck` image variant required for gaming mode
- **ChimeraOS**: Chimera web app (local frontend, downloads compatibility data at session start); read-only root via overlay mounts
- **CachyOS**: `Proton-CachyOS` (bleeding-edge + wine-staging + FSR + UMU); LAVD CPU scheduler (handheld); NTSync enabled by default
- **Nobara**: `falcond.service` (per-game daemon: SCX scheduler selection, AMD 3D VCache mode, per-game scripts); `kde-steamdeck-additions` (Nested Desktop mode); `gamescope-session-common` (TDP/FPS/upscaling toggles from within session)

## systemd Session Architecture

Gaming mode ≠ desktop mode. **`graphical-session.target` is NOT activated by gamescope.**

```
DESKTOP MODE                     GAMING MODE
─────────────────                ──────────────────────
graphical-session.target  ✓      gamescope-session.target  ✓
plasma-workspace.target   ✓      graphical-session.target  ✗  ← NOT active
```

**Service wiring rule:** Any user service that must run in gaming mode needs:
```ini
[Install]
WantedBy=gamescope-session.target
```
Add `graphical-session.target` too for dual-mode operation. Services with only `WantedBy=graphical-session.target` silently skip in gaming mode — no error, no log.

### Session target names by distro

| Distro | Primary gaming target |
|--------|-----------------------|
| SteamOS / Bazzite | `gamescope-session.target` |
| ChimeraOS | `gamescope-session.target` (via `gamescope-session-plus`) |
| CachyOS | `gamescope-session-cachyos.target` |
| Nobara | `gamescope-session.target` |

## Steam Linux Runtime (SLR)

Every Proton game runs inside an SLR container. The runtime version is determined by the Proton version.

| Version | Codename | Isolation | Used by |
|---------|----------|-----------|---------|
| SLR 1.0 | **scout** | `LD_LIBRARY_PATH` injection (no container) | Legacy Proton ≤5.0, old native |
| SLR 2.0 | **soldier** | Linux namespace container | Proton 5.13–7.0 |
| SLR 3.0 | **sniper** | Linux namespace container | Proton 8–10, older native |
| SLR 4.0 | **steamrt4** | Linux namespace container | Proton 11+, new native |

**Scout (SLR 1.0) is the source of most Arch/rolling-release runtime problems.** It injects its own shared library stack via `LD_LIBRARY_PATH`. Mixing scout libs with system libs → crashes, silent failures, audio issues. Sniper/steamrt4 (container isolation) avoid this entirely.

### Runtime paths
```
~/.steam/root/ubuntu12_32/steam-runtime/   # Scout (SLR 1.0)
# Sniper/soldier/steamrt4 are Steam Play compat tools, not at fixed paths
```

### `steam-native` (Arch-based distros only)
`STEAM_RUNTIME=0` / `steam-native` bypasses the bundled runtime entirely — uses system libraries only. Requires 130+ system packages. Use only when debugging runtime-specific issues; not for daily use.

## Critical Environment Variables

| Variable | Source | Effect | Common issue |
|----------|--------|--------|-------------|
| `LD_PRELOAD` | Steam wrapper | Injects gameoverlayrenderer.so | **Lag bomb at ~24 min** without Steam Overlay; clear with `LD_PRELOAD="" %COMMAND%` |
| `WAYLAND_DISPLAY` | Desktop session | Tells gamescope which Wayland socket to use | If leaked from the desktop compositor, gamescope picks **nested** backend instead of KMS → games render into nonexistent compositor → fail |
| `STEAM_RUNTIME` | Manual | `0` = bypass bundled libs | Useful for debugging; breaks many games |
| `MESA_VK_DEVICE_SELECT` | Manual | Selects Vulkan GPU | Needed on multi-GPU systems to force discrete |
| Daemon-guard vars (e.g. `FOO_DAEMON=1` in `/etc/profile.d/`) | Login shell | Daemon spawn guards | Any daemon-guard var inherited from login env can fork-bomb if the daemon spawns child processes before its socket is ready |
| `PROTON_USE_NTSYNC` | Launch options | `0` = disable NTSync (CachyOS default-on) | Fallback for games broken by NTSync |
| `PROTON_NO_FSYNC=1` | Launch options | Disable FSYNC, fall back to ESYNC | Workaround for FSYNC-broken games |
| `STEAM_COMPAT_DATA_PATH` | Launch options | Override prefix path | Share prefix between shortcuts |

### Gamescope key flags
```bash
gamescope -W 1920 -H 1080   # output resolution
         -w 1280 -h 720      # game (render) resolution
         -r 60               # framerate cap
         -f                  # fullscreen at launch (avoids Meta+f perf bug)
         -e                  # Steam integration (propagates to child games)
         -F fsr              # AMD FSR 1.0 upscaling
         -F nis              # NVIDIA NIS upscaling
         --hdr-enabled        # HDR10 (embedded/KMS mode only)
         --adaptive-sync      # VRR/FreeSync/G-Sync
         --mangoapp           # MangoHud via gamescope compositing (NOT standard MangoHud)
         --expose-wayland     # enable Wayland client support
```

## Common Failure Patterns (Distilled)

### 1. Gamescope can't open DRM — session not starting

**Symptoms:** `Could not take device: Device or resource busy` → `Could not open KMS device` → `Failed to create backend` → SIGSEGV → login manager storm

**Root cause pattern:** A seatless process inherited the user manager *before* the real seat0 login. logind grants DRM master only to the session active on seat0 — the seatless process is denied.

**Common triggers:**
- `loginctl enable-linger` set → seatless ghost session spawned at boot → race with real login
- Another compositor (Plasma, Xorg) still holding DRM when gamescope starts
- Running gamescope from a non-seat session (SSH, systemd service not on seat)

**Diagnose:** `loginctl list-sessions` → look for `class=manager` with no seat; `sudo fuser -v /dev/dri/card*`

### 2. Services silently skip in gaming mode

**Cause:** `WantedBy=graphical-session.target` only. Gaming mode never activates this target.

**Fix:** Add `WantedBy=gamescope-session.target` to the `[Install]` section. User drop-in at `~/.config/systemd/user/<service>.d/gaming-mode.conf`.

### 3. WAYLAND_DISPLAY leaked → gamescope picks wrong backend

**Cause:** The desktop compositor (e.g. KDE Plasma) leaks `WAYLAND_DISPLAY=wayland-0` into the user manager environment. Gamescope auto-detects it → tries nested Wayland backend → connects to compositor that isn't there → exits 1.

**Fix:** Drop-in that unsets it:
```ini
[Service]
UnsetEnvironment=DISPLAY XAUTHORITY WAYLAND_DISPLAY
```

### 4. LD_PRELOAD lag bomb at ~24 min

**Cause:** Steam wrapper sets `LD_PRELOAD` for gameoverlayrenderer. Injected library causes periodic GC/stutter cycle.

**Fix (Official):** Enable Steam Overlay for the game. Or: `LD_PRELOAD="" %COMMAND%` in launch options.

### 5. "non-Gamescope swapchain" Vulkan popup

```
CreateSwapchainKHR: Creating swapchain for non-Gamescope swapchain.
Hooking has failed somewhere!
```

**Cause:** Game launched but gamescope isn't running (boot failed, or running on desktop). `VkLayer_FROG_gamescope_wsi` is a global Vulkan layer that warns when it doesn't detect gamescope. Not a corrupt prefix.

**Fix:** Fix the underlying reason gamescope didn't start. Remove `DISABLE_GAMESCOPE_WSI=1` band-aids once gamescope is working — that flag disables VRR/HDR/scaling handoff.

### 6. SLR container (bwrap) fails to start

**Cause:** Steam's pressure-vessel (bubblewrap) bind-mounts every existing mount point. A stale/unavailable mount (offline NAS, broken automount) causes the entire container to fail.

**Diagnose:** `mount | grep -E 'autofs|cifs|nfs'`; `ls -la /mnt/` (look for `?` entries)

**Fix:** Disable or remove the unavailable fstab entry; `sudo systemctl daemon-reload`.

### 7. Plugin manager (Decky) not running in gaming mode

**Cause:** `plugin_loader.service` has `WantedBy=graphical-session.target` only.

**Fix:** Ensure service is enabled for the correct gamescope target. On Bazzite: `ujust setup-decky` handles this. On others: check service install section and add gaming mode target.
