# Source References

Links used to build this skill. **Sites blocked to plain headless fetchers** (curl, basic WebFetch):
- `wiki.archlinux.org` — Anubis JS proof-of-work challenge blocks simple scrapers
- `docs.bazzite.gg`, `wiki.cachyos.org`, `wiki.nobaraproject.org` — return 403
- `wiki.hyprland.org` — may block depending on request headers

## How an agent CAN access these sources

| Source | Method | Notes |
|--------|--------|-------|
| **ProtonDB** | Direct JSON API — no tool needed | `curl https://www.protondb.com/api/v1/reports/summaries/<APPID>.json` → tier/score/confidence. Unofficial but stable. Find AppID in `steamapps/appmanifest_*.acf` or the store URL |
| **Arch Wiki (offline)** | `pacman -S arch-wiki-docs` | Full wiki HTML at `/usr/share/doc/arch-wiki/html/en/` — agent greps/reads local files, zero network. Add `wikiman` for terminal search |
| **Arch Wiki (online)** | Tavily MCP `tavily_extract`, or Firecrawl | Both fetch via their own infrastructure and pass the Anubis challenge (verified working) |
| **Bazzite/CachyOS/Nobara docs** | Tavily MCP `tavily_extract`, or Firecrawl | Verified working on docs.bazzite.gg |
| **Any JS-challenged site (fallback)** | Playwright MCP (`npx @playwright/mcp@latest`) | Real headless browser, executes the challenge JS; heaviest option |

Order of preference: local package > direct API > extraction service (Tavily/Firecrawl) > headless browser.

## Valve / Steam official
- https://github.com/ValveSoftware/gamescope — gamescope source + README (architecture, flags, known bugs)
- https://github.com/ValveSoftware/steam-runtime — SLR source + runtime version docs
- https://github.com/ValveSoftware/Proton — Proton source
- https://github.com/ValveSoftware/steam-for-linux — Steam Linux client bug tracker
- https://github.com/ValveSoftware/steam-audio — Steam Audio (HRTF/spatial audio SDK)
- https://github.com/ValveSoftware/GameNetworkingSockets — networking library
- https://partner.steamgames.com/doc/store/application/platforms/linux — Steamworks Linux dev guide
- https://partner.steamgames.com/doc/home — Steamworks documentation root
- https://partner.steamgames.com/doc/sdk/api — Steamworks API reference
- https://help.steampowered.com/en/faqs/view/69E3-14AF-9764-4C28 — Steam Linux FAQ
- https://help.steampowered.com/en/faqs/view/7DD4-C618-182E-0E49 — Steam Linux FAQ (2)

## Arch Wiki (open in browser — blocked to scrapers)
- https://wiki.archlinux.org/title/Steam — Steam on Arch: install, runtime, config
- https://wiki.archlinux.org/title/Steam/Troubleshooting — **primary troubleshooting reference**
- https://wiki.archlinux.org/title/Steam/Game-specific_troubleshooting — per-game fixes (FMOD, specific titles)
- https://wiki.archlinux.org/title/Steam#Steam_Remote_Play — Remote Play setup
- https://wiki.archlinux.org/title/Gamescope — Gamescope setup, flags, session, HDR
- https://wiki.archlinux.org/title/GameMode — GameMode daemon config
- https://wiki.archlinux.org/title/MangoHud — MangoHud overlay config
- https://wiki.archlinux.org/title/Gaming — general Linux gaming overview
- https://wiki.archlinux.org/title/AMDGPU — AMD kernel module params, power management, overclocking
- https://wiki.archlinux.org/title/PipeWire — PipeWire audio config, WirePlumber
- https://wiki.archlinux.org/title/Advanced_Linux_Sound_Architecture/Troubleshooting — ALSA debugging
- https://wiki.archlinux.org/title/HDR_monitor_support — HDR full reference (compositor, app, monitor requirements)
- https://wiki.archlinux.org/title/Hardware_raytracing — raytracing per GPU vendor, RADV/VKD3D flags
- https://wiki.archlinux.org/title/Wine — Wine setup, Winetricks, prefix management
- https://wiki.archlinux.org/title/Hybrid_graphics — PRIME, multi-GPU laptop setup
- https://wiki.archlinux.org/title/CPU_frequency_scaling — CPU governor, power profiles
- https://wiki.archlinux.org/title/Dynamic_Kernel_Module_Support — DKMS module rebuild after kernel upgrades
- https://wiki.archlinux.org/title/Steam_Deck — Steam Deck Linux specifics
- https://wiki.archlinux.org/title/NVIDIA_GeForce_NOW — GeForce NOW cloud gaming on Linux
- https://wiki.archlinux.org/title/Video_game_platform_emulators — emulator list (RetroArch, Dolphin, etc.)
- https://wiki.archlinux.org/title/System_maintenance — Arch maintenance best practices

## Distro documentation
- https://docs.bazzite.gg/ — Bazzite full docs
- https://docs.bazzite.gg/General/FAQ/ — Bazzite FAQ
- https://github.com/ChimeraOS/chimeraos/wiki — ChimeraOS wiki
- https://wiki.nobaraproject.org/ — Nobara wiki
- https://wiki.cachyos.org/cachyos_basic/faq/ — CachyOS FAQ
- https://wiki.cachyos.org/configuration/automount_with_fstab/ — CachyOS fstab/automount

## Compatibility databases
- https://areweanticheatyet.com/ — per-game anti-cheat Linux compatibility
- https://www.protondb.com/ — crowdsourced Proton compatibility reports
- https://www.protondb.com/help/improving-performance — ProtonDB performance guide
- https://www.protondb.com/help/troubleshooting-faq — ProtonDB troubleshooting FAQ

## AMD GPU
- https://amdgpu-install.readthedocs.io/en/latest/ — amdgpu-install tool docs
- https://www.amd.com/de/resources/support-articles/knowledge-base-search.html — AMD KB articles
- https://www.kernel.org/doc/html/latest/gpu/amdgpu/thermal.html — AMD GPU Power/Thermal Controls sysfs (kernel docs)

## Wayland / color management
- https://gitlab.freedesktop.org/wayland/wayland-protocols/-/merge_requests/14 — color-management protocol MR (scRGB/HDR foundation)
- https://gitlab.freedesktop.org/pq/color-and-hdr — color/HDR protocol docs

## Hyprland (for desktop-mode Steam users on Hyprland)
- https://wiki.hyprland.org/Configuring/Variables/ — Hyprland config variables reference
- https://wiki.hyprland.org/Configuring/Monitors/ — multi-monitor setup (relevant for Big Picture + desktop dual-monitor)

## Performance / tooling
- https://aur.archlinux.org/packages/schedtoold — schedtool AUR package
- https://github.com/freequaos/schedtool — schedtool source
- https://pwr-solaar.github.io/Solaar/ — Solaar (Logitech peripheral manager)
- https://github.com/libratbag/piper — Piper (gaming mouse config)

## Remote play / streaming
- https://moonlight-stream.org/ — Moonlight (NVIDIA GameStream client)
- https://parsec.app/ — Parsec (cloud gaming / remote desktop)

## Community
- https://www.reddit.com/r/linux_gaming/ — r/linux_gaming
- https://www.reddit.com/r/linux_gaming/wiki/index/ — r/linux_gaming wiki index
- https://www.reddit.com/r/linux_gaming/wiki/faq/ — r/linux_gaming FAQ
- https://github.com/AdelKS/LinuxGamingGuide — comprehensive Linux gaming guide

## Hardware teardown
- https://www.ifixit.com/Device/Steam_Game_Console — Steam Deck iFixit teardown

## APIs / standards
- https://en.wikipedia.org/wiki/Vulkan — Vulkan overview
- https://en.wikipedia.org/wiki/OpenGL — OpenGL overview
- https://en.wikipedia.org/wiki/Cloud_gaming — cloud gaming overview
