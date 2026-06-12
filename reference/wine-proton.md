# Wine & Proton — Prefixes, Troubleshooting, Anti-Cheat, Cloud Gaming

## Proton Troubleshooting

**First: always check [ProtonDB](https://www.protondb.com) for the specific game before doing anything else.** Search by game name — user reports often list the exact launch options and fixes that work.

### Quick-start launch options (add in Steam → game Properties → Launch Options)

```bash
PROTON_LOG=1 %command%               # write detailed log to ~/steam-<ID>.log
PROTON_USE_WINED3D11=1 %command%     # bypass DXVK, use wined3d for D3D11 (slower but fixes some crashes)
PROTON_NO_ESYNC=1 %command%          # disable esync (fix: crash after playing a while)
PROTON_NO_FSYNC=1 %command%          # disable fsync
unset LC_ALL && %command%            # fix save game crashes (locale conflict)
LD_PRELOAD="" %command%              # fix ~24-min lag spike
LD_BIND_NOW=1 %command%              # pre-bind libs at startup; reduces first-call latency
```

### Common Proton failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Crash after ~30 min | LD_PRELOAD lag bomb | `LD_PRELOAD="" %command%` |
| Crash after a while (esync) | `ulimit -Hn` ≤ 4096 | Raise `nofile` limit in `/etc/security/limits.conf`; or `PROTON_NO_ESYNC=1` |
| No text in game | Missing Windows fonts | Upgrade Proton (fixed in 3.16-4+) |
| Missing textures (e.g., Witcher 3) | Old DXVK/Vulkan | Upgrade Mesa (≥18.3) + DXVK (≥0.90) |
| Sound crackling | xaudio2 missing | `protontricks <appid> xact`; or `WINEDLLOVERRIDES=xaudio2_7=n,b` |
| Save game crash | Locale conflict | `unset LC_ALL && %command%` |
| Stutter at game start | DXVK shader cache building | Normal; wait for it to complete (one-time per game) |
| Full system hang | GPU hang | Test with plain Wine; if reproduced, file against Mesa/driver |
| Game on NTFS won't start | NTFS mounted root-only | Remount with user permissions or move game to ext4/btrfs (see `steam-client.md` → NTFS) |

### Modifying game prefixes

```bash
# Run Winetricks in a game's prefix
WINEPREFIX=~/.steam/root/steamapps/compatdata/<APPID>/pfx/ winetricks

# Protontricks (Valve-blessed wrapper)
protontricks <APPID> <verb>             # install Windows component into prefix
protontricks-launch --appid <APPID> <exe>  # run .exe inside prefix

# Check which Proton version last ran this prefix
cat ~/.steam/root/steamapps/compatdata/<APPID>/version
```

**Forcing Proton when native Linux build exists:** Properties → Compatibility → "Force the use of a specific Steam Play compatibility tool". Useful when native build is outdated or crashes.

**Nuclear prefix reset** (when all else fails): delete `~/.steam/root/steamapps/compatdata/<APPID>/pfx/` — Steam rebuilds it on next launch. Loses save games stored in prefix (check for cloud saves first).

## Wine / Native Prefix Tools

Wine is a Win32 API implementation — not emulation, not virtualization. Performance penalty vs Windows varies per game.

⚠️ Wine is not sandboxed — it has the same filesystem access as your user. Never run untrusted Windows executables in Wine unless isolated.

### Prefix management

```bash
# Default prefix location
~/.wine/

# Override prefix per-game
WINEPREFIX=~/.wine-gamename wine executable.exe

# Config tools (run inside the prefix's context)
wine winecfg     # Wine configuration (audio, libraries, Windows version)
wine control     # Windows Control Panel equivalent
wine regedit     # Registry editor
```

**Prefixes are not forward-compatible** — upgrading Wine auto-upgrades old prefixes; they may break on old Wine. Treat game prefixes as disposable unless they hold important saves.

Use **separate prefixes per game** for dependency isolation — conflicting DLLs in one prefix don't affect others.

**Nuclear prefix reset:** delete the `pfx/` directory (`~/.wine` for bare Wine, `~/.steam/root/steamapps/compatdata/<APPID>/pfx/` for Proton). Steam/Wine recreates it on next launch.

### System-level optional dependencies

Install before running Wine apps that need these features:

| Feature | Package(s) |
|---------|-----------|
| Encryption / HTTPS | `gnutls` |
| Gamepad / joystick | `sdl2-compat` |
| Video playback | `gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly ffmpeg` |
| NTLM/SMB auth | `samba` |
| Internet Explorer compat | `wine-gecko` |
| .NET apps | `wine-mono` |

### In-prefix dependencies (winetricks verbs)

Many games need Windows components installed **into** the prefix:

```bash
winetricks <verb>              # generic
winetricks --help              # list all verbs
```

Common gaming verbs:
- `xact` — XAudio (most common fix for no sound)
- `dsound directmusic gmdls` — DirectSound + MIDI for 90s games
- `d3dx9` / `d3dx11` — DirectX 9/11 DLLs
- `vcrun2019` / `vcrun2022` — Visual C++ runtimes
- `dotnet48` — .NET Framework 4.8
- `mfc140` — MFC runtime (various installers)
- `corefonts` — Microsoft fonts (fixes missing text)

**Find what a game needs:** check [Wine AppDB](https://appdb.winehq.org/), [Lutris install scripts](https://lutris.net), [Bottles repo](https://github.com/bottlesdevs/components), or ProtonDB user reports.

### Wine managers (all support gamescope "Use Gamescope" toggle)

| Tool | Use case |
|------|---------|
| **Lutris** | Multi-source game manager (Wine, native, emulators); install scripts automate prefix setup |
| **Bottles** | GTK4 prefix manager; isolated environments; dependency manager UI |
| **Heroic** | GOG + Epic Games Store + Amazon launcher; integrates umu-launcher/Proton |
| **protonup-qt** | Manage GE-Proton, Wine-GE, and Lutris runners — install/remove from GUI |
| **umu-launcher** | CLI Proton runner outside Steam; backend used by Heroic/Lutris |
| **PlayOnLinux** | Older prefix manager; superseded by Bottles for most use cases |
| **portproton** | Russian Linux gaming wrapper |

### Wine builds for gaming

| Build | Notes |
|-------|-------|
| `wine` (AUR: development) | Upstream latest |
| `wine-staging` | Staging patches: bug fixes + experimental features not yet upstream |
| `wine-tkg` | Custom build: staging + esync/fsync/ntsync + game-specific patches |
| `wine-cachyos` | CachyOS's bleeding-edge build (wine-staging + FSR + UMU) |
| `proton-ge-custom` | GE-Proton: Proton fork with additional media codecs + game fixes |

### DLL overrides (WINEDLLOVERRIDES)

```bash
# Format: "dll=native,builtin" or "dll=builtin,native" or "dll=n,b"
WINEDLLOVERRIDES="xaudio2_7=n,b" wine game.exe   # use native xaudio2_7, fall back to built-in
WINEDLLOVERRIDES="d3d11=n" wine game.exe          # force native D3D11 (e.g. for custom DXVK)
```

In winecfg: Libraries tab → add override per-DLL.

### MIDI support for old games

90s/00s games often used MIDI for music:
```bash
winetricks gmdls dsound directmusic  # install MIDI DLS collection + DirectSound + DirectMusic
```
System MIDI must be configured first: check `aplaymidi -l` for available ports.

## Anti-Cheat Compatibility

Check any game first at **[areweanticheatyet.com](https://areweanticheatyet.com)**.

| Anti-Cheat | Status | Technical reason |
|-----------|--------|-----------------|
| **VAC** (Valve) | ✅ Works | Server-side; no kernel driver |
| **Easy Anti-Cheat (EAC)** | ✅ Most games | EAC ships native Linux `.so`; Proton loads it directly. Developer must opt-in per-title |
| **BattlEye** | ✅ Many games | Same mechanism as EAC; opt-in per-title |
| **Vanguard** (Riot) | ❌ Blocked | Kernel-level ring-0 driver; explicitly checks for non-Windows kernel → blocks |
| **Hyperion** (EA/Apex) | ❌ Blocked | Kernel-level; blocks Linux |
| **nProtect GameGuard** | ❌ Broken | Kernel driver; cannot run in Wine |
| **FairFight** | ❌ Denied | Server-side behavior analysis + client checks that fail |

**~55% of anti-cheat protected games are non-functional on Linux** (areweanticheatyet.com). This is a hard limit — no Proton tweak or compatibility layer fixes kernel-level AC. Inform the user clearly before suggesting workarounds.

**Notable working games:** Halo MCC (EAC), ARK: Survival Evolved (EAC), Dead by Daylight (EAC), Elden Ring (no AC), most single-player games.

**Not working:** Fortnite (Vanguard), Valorant (Vanguard), Apex Legends (Hyperion).

## Cloud Gaming (GeForce NOW / alternatives)

For games with kernel-level anti-cheat (Fortnite, Valorant) that cannot run natively on Linux, cloud gaming is the only option.

| Service | Linux support | Notes |
|---------|--------------|-------|
| **GeForce NOW** | ✅ Flatpak or Chromium browser | NVIDIA streams from cloud; Chromium works OOTB; keyboard layout may need workaround |
| **Xbox Cloud Gaming** | ✅ Browser (Chromium/Edge) | No dedicated Linux app |
| **Parsec** | ✅ Native app | Peer-to-peer; stream your own gaming PC |
| **Moonlight** | ✅ Native app | NVIDIA GameStream client; works with Sunshine as server (Sunshine = open-source host) |

**GeForce NOW on Arch (Flatpak):**
```bash
flatpak remote-add --if-not-exists GeForceNOW https://international.download.nvidia.com/GFNLinux/flatpak/geforcenow.flatpakrepo
flatpak install GeForceNOW com.nvidia.geforcenow
```
