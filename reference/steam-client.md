# Steam Client — Installation, Layout, Error Reference

## Steam Installation (Arch-based)

```bash
# Enable multilib repo first (required for 32-bit support)
# /etc/pacman.conf → uncomment [multilib] section

pacman -S steam

# Prerequisites Steam checks at startup:
# - lib32 OpenGL driver (lib32-mesa for AMD, lib32-nvidia-utils for NVIDIA — match vendor!)
# - en_US.UTF-8 locale (locale-gen)
# - xdg-desktop-portal + backend (for file chooser when adding library folders)
# - systemd-resolved symlink: ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
# - NetworkManager (required for Big Picture / gaming mode network panels)
# - vm.max_map_count increase (some games crash without it):
#   echo "vm.max_map_count=2147483642" | sudo tee /etc/sysctl.d/80-gamecompat.conf
```

**Directory layout:**
```
~/.local/share/Steam/          # default install (also accessible via ~/.steam/root symlink)
~/.local/share/Steam/steamapps/common/         # game files
~/.local/share/Steam/steamapps/compatdata/     # Proton prefixes (one dir per AppID)
~/.local/share/Steam/config/localconfig.vdf    # per-game settings
```

**Launch options format:**
```bash
%command%                                    # required token for prefix/suffix
FOO=bar %command%                            # set env var
gamemoderun mangohud %command%               # wrap command
gamemoderun mangohud %command% -option       # wrap + args
othercommand # %command%                     # replace command entirely (# comments out original)
```

**Proton outside Steam:** use `umu-launcher` (Heroic and Lutris support it natively as backend).

**Managing Proton versions / GE-Proton:** use `protonup-qt` GUI or `protonup-cli`.

**vm.max_map_count:** needed for games like Elden Ring, DCS World. Set permanently:
```bash
echo "vm.max_map_count=2147483642" | sudo tee /etc/sysctl.d/80-gamecompat.conf && sudo sysctl --system
```

## Runtime / library errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `GLIBCXX_3.X.XX not found` | Scout runtime ships outdated `libstdc++.so.6` | See "Finding missing runtime libraries" debugging commands below |
| `SDL not found` / SDL thread priority warning | lib32-sdl2 missing | Install `lib32-sdl2` |
| `munmap_chunk(): invalid pointer` / `free(): invalid pointer` | Game not recently updated, scout runtime disabled | Replace game's `libsteam_api.so` with one from a working game |
| `terminate called after throwing an instance of 'dxvk::DxvkError'` | Conflicting Vulkan drivers installed | `lib32-vulkan-intel` and NVIDIA Vulkan are mutually exclusive; remove the unneeded one. Check: `pacman -Qs vulkan`; find vendor: `lshw -C display \| grep vendor` |
| `failed to dlopen engine.so … libgcc_s.so.1: version GCC_7.0.0 not found` | Incompatible bundled libgcc in game dir | `mv .local/share/Steam/steamapps/common/GAME/bin/libgcc_s.so.1{,.b}` |
| `version CURL_OPENSSL_3 not found` | curl compat missing | Install `libcurl-compat` / `lib32-libcurl-compat`; symlink: `ln -s /usr/lib/libcurl-compat.so.4.4.0 GAMEPATH/lib/libcurl.so.4` |
| Steam webview / Friends black screen (native runtime) | Missing libpcre in native runtime | `LD_PRELOAD="/usr/lib/libgio-2.0.so.0 /usr/lib/libglib-2.0.so.0" steam-native` or add `-no-cef-sandbox` flag |
| `Steam: An X Error occurred` / `GLXBadContext` | lib32-nvidia driver version mismatch with main driver | `pacman -Qs nvidia` — versions must match exactly; or remove `config.vdf`: `rm ~/.local/share/Steam/config/config.vdf` |
| Compatibility tool configuration failed | Broken Proton / SLR install | Steam Library → Tools → right-click each Proton + SLR → Verify integrity of tool files |
| Game starts but closes immediately (custom kernel) | User namespaces disabled | Enable `CONFIG_USER_NS` in kernel config |
| Steam Library won't open / `Assertion 'device' failed` | `lib32-libnm` missing (systemd 253.5-2+) | Install `lib32-libnm` |
| Periodic lag spikes / low FPS after ~30 min | `LD_PRELOAD` Steam overlay injection | Launch option: `LD_PRELOAD="" %command%` |
| `ERROR: ld.so: gameoverlayrenderer.so … wrong ELF class: ELFCLASS32` | Steam loads both 32/64-bit; one fails | Safely ignorable — not an actual error |
| Poor performance / stutter right after Steam launch | Bugged Proton under appid 0 | Remove `~/.steam/root/steamapps/compatdata/0`; also remove old GE-Proton ≤5.21-GE-1 |
| `symbol lookup error: libxcb-dri3.so.0: undefined symbol` | DRI3 incompatibility | Launch with `LIBGL_DRI3_DISABLE=1` |
| `"could not determine 32/64 bit of java"` | `linux-steam-integration` package conflict | Uninstall `linux-steam-integration` |

## Graphical issues

| Symptom | Fix |
|---------|-----|
| Steam blurry on HiDPI Xwayland | Run nested gamescope: `gamescope -f -m 1 -e -- steam -gamepadui`; or set `xwayland { force_zero_scaling = true }` (Hyprland) |
| Steam flickers / black screen (dual GPU, Wayland) | `PrefersNonDefaultGPU=false` in `~/.local/share/applications/steam.desktop` |
| Intel iGPU: web views don't render (Wayland) | Settings → Interface → disable "Enable GPU accelerated rendering in web views" |
| Vulkan stutters every 1–2 sec | vsync conflict; add `DXVK_FRAME_RATE=60 %command%` |
| OpenGL version too low (Mesa) | `MESA_GL_VERSION_OVERRIDE=4.1 MESA_GLSL_VERSION_OVERRIDE=410 %command%` |
| Old Intel hardware (GMA/Westmere) crashes | `MESA_GL_VERSION_OVERRIDE=3.1 MESA_GLSL_VERSION_OVERRIDE=140 %command%` |
| Some games freeze at start (NVIDIA 535 + DXVK + Xorg) | Disable `ForceFullCompositionPipeline` or downgrade NVIDIA driver |
| DirectX errors on Intel/NVIDIA hybrid laptop | Configure PRIME (see `gpu.md`); or force WineD3D: `PROTON_USE_WINED3D=1 %command%` |
| Text missing / corrupt | Install `lib32-fontconfig`, `ttf-liberation`, `xorg-fonts-misc` |
| Big Picture minimizes on focus loss (Remote Play / multi-monitor) | `SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0 %command%` |

## Client-level audio issues

(Full audio reference: `audio.md`)

| Symptom | Fix |
|---------|-----|
| No audio / segfault (old ALSA) | Rename `~/.steam/steam/ubuntu12_32/steam-runtime/i386/usr/lib/i386-linux-gnu/alsa-lib/`; or `LD_PRELOAD='/usr/$LIB/libasound.so.2' steam` |
| PipeWire 32-bit audio missing | Install `lib32-pipewire` |
| FMOD crackling (Hotline Miami, Transistor) | Set correct default ALSA card in `/etc/asound.conf` |
| OpenAL streams can't move between devices | Add `[pulse]\nallow-moves=true` to `~/.alsoftrc` |
| Crackling microphone in Steam Voice / games | Launch with `PULSE_LATENCY_MSEC=30` |

## Steam client issues

| Symptom | Fix |
|---------|-----|
| Empty file browser when adding library | Timestamp issue: `stat <path>` — if future timestamp, `touch <path>` to reset |
| "Must be on filesystem with execute permissions" | Add `exec` after `user`/`users` in fstab; ensure folder is named `steamapps` (lowercase) |
| Unusually slow downloads | Install `dnsmasq`; or disable HTTP2: `echo "@nClientDownloadEnableHTTP2PlatformLinux 0" > ~/.steam/steam/steam_dev.cfg` |
| "Needs to be online" error while online | Install `lib32-systemd`; check DNS with `systemd-resolved`; `resolvectl flush-caches` |
| Steam forgets password | After login: `chattr +i ~/.steam/registry.vdf` (makes file immutable) |
| `/tmp/dumps/` fills up disk on crash loop | `ln -s /dev/null /tmp/dumps` |
| No join/invite context menu | Install `lsof` |
| Slow / sluggish UI | Disable "GPU accelerated web views" (Settings → Interface); move friends list to second monitor; disable animated avatars |
| Missing taskbar menu | Install `libappindicator-gtk2` + `lib32-libappindicator-gtk2` |
| Cannot access store (-105 / -102) | `resolvectl flush-caches`; ensure `systemd-resolved` running and `/etc/resolv.conf` symlinked |
| Broken install (various) | `steam --reset` |
| Very long startup / frozen UI | Edit `/etc/nsswitch.conf`: change `mdns` → `mdns_minimal`; restart `systemd-resolved` |
| Steam hangs on "Installing breakpad exception handler" (NVIDIA) | lib32-nvidia version mismatch with main driver |
| Games no internet in Proton 5.13+ | `systemd-resolved` symlink missing: `ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf` |
| "SetLocale('en_US.UTF-8') fails" | Generate locale: add `en_US.UTF-8 UTF-8` to `/etc/locale.gen`, run `locale-gen` |
| File picker only shows Steam library | Install `xdg-desktop-portal` |
| Steam Beta breaking bugs | `rm -f ~/.local/share/Steam/package/beta` to revert to stable |

## NTFS / filesystem

| Symptom | Fix |
|---------|-----|
| Games on NTFS won't start (Wine colon paths) | Use `ntfs3` kernel driver (not `ntfs-3g`) with `windows_names` mount option; or move `compatdata/` and Proton to ext4/btrfs and symlink back |
| 2K games (Civ5) fail on XFS | Move game or library to ext4/btrfs |
| Corrupted prefix on NTFS shared with Windows | `ntfs3` + `windows_names` prevents illegal-character collisions; move `compatdata/` off NTFS entirely if recurring |

## Remote Play

| Symptom | Fix |
|---------|-----|
| Remote Play crashes (Arch host → Arch guest) | Install `lib32-libcanberra` |
| Hardware decoding unavailable | Install `libva` + `lib32-libva`; Intel also needs `libva-intel-driver` + `lib32-libva-intel-driver`; may need to delete `~/.local/share/Steam/ubuntu12_32/steam-runtime/i386/usr/lib/i386-linux-gnu/libva*` to force system libs |

## Debugging tools

```bash
# Find what libraries a game binary needs
ldd ~/.steam/root/steamapps/common/GAME/GAME_EXECUTABLE

# Find missing libraries in scout runtime (when using steam-native)
cd ~/.steam/root/ubuntu12_32
file * | grep ELF | cut -d: -f1 | LD_LIBRARY_PATH=. xargs ldd | grep 'not found' | sort | uniq

# See which non-system libraries Steam is using live
for i in $(pgrep steam); do sed '/\.local/!d;s/.*  //g' /proc/$i/maps; done | sort | uniq

# Launch Steam with debugger
DEBUGGER=gdb steam    # then type 'run', on crash type 'backtrace'

# Reset broken Steam install
steam --reset
```
