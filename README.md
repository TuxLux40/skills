# steam-debugger

Agent skill for troubleshooting **Steam on Linux gaming distros** — SteamOS, Bazzite, ChimeraOS, CachyOS, Nobara, and plain Arch.

Built for [Claude Code](https://claude.com/claude-code) and other agents that support the [Agent Skills](https://agentskills.io) format, but the reference files are plain markdown and useful to humans directly.

## What it covers

- **Gamescope session architecture** — embedded vs nested mode, DRM/KMS ownership, the seven recurring failure patterns (DRM master conflicts, linger ghost sessions, `WAYLAND_DISPLAY` pollution, services silently skipping gaming mode, …)
- **Steam client** — installation, runtime/library error tables, NTFS issues, Remote Play
- **Steam Linux Runtime** — scout/soldier/sniper/steamrt4 and why scout breaks rolling-release distros
- **Proton & Wine** — launch options, prefix management, winetricks, DLL overrides, builds and managers
- **Anti-cheat** — what works (EAC/BattlEye opt-in), what never will (Vanguard/Hyperion), cloud-gaming escape hatch
- **AMD GPU** — kernel module parameters, power management sysfs, known hardware issues, RADV
- **Audio** — PipeWire/WirePlumber architecture, failure table, ALSA fallback debugging
- **Performance** — GameMode, MangoHud, CPU governors, scheduler tuning
- **Display** — HDR setup per Proton variant, VRR, hardware raytracing, Wayland color management
- **Steam Deck** — hardware IDs, firmware shortcuts, OLED audio on plain Arch

## Layout

```
SKILL.md                 entry point: triage protocol, symptom routing, fix tiers
reference/               per-domain knowledge files (loaded on demand)
scripts/                 read-only diagnostic evidence collectors (POSIX sh)
```

The skill is **triage-first**: it instructs the agent to ask intake questions before suggesting fixes, label every fix with a risk tier (✅ official / ⚠️ community / 🔴 deep), and explain commands to non-expert users.

The diagnostic scripts mutate nothing. They collect logind/DRM/GPU/audio state in one pass and degrade gracefully when tools are missing.

## Install (Claude Code)

```bash
git clone https://github.com/YOURUSER/steam-debugger ~/.claude/skills/steam-debugger
```

Claude Code discovers skills in `~/.claude/skills/` automatically. Per-project install: clone into `.claude/skills/` inside the project instead.

## Sources

Distilled from the Arch Wiki (Steam, Gamescope, AMDGPU, PipeWire, Wine, HDR, and ~15 more pages), Valve's gamescope/steam-runtime/Proton repositories, ProtonDB guides, distro documentation, and kernel.org GPU docs. Full link list with scraper-accessibility notes: [`reference/sources.md`](reference/sources.md).

Note: several primary sources (wiki.archlinux.org, docs.bazzite.gg, wiki.cachyos.org, wiki.nobaraproject.org) block automated fetchers — one motivation for this skill being fully self-contained.

## License

CC-BY-SA 4.0 — substantial portions derive from the [Arch Wiki](https://wiki.archlinux.org), which is licensed CC-BY-SA.
