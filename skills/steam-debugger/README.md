# steam-debugger

Agent skill for debugging **Steam on Linux gaming distros** — SteamOS, Bazzite, ChimeraOS, CachyOS, Nobara, plain Arch.

Built for [Claude Code](https://claude.com/claude-code) and any agent speaking the [Agent Skills](https://agentskills.io) format. Reference files are plain markdown — useful to humans without any agent.

## Why this exists

Linux gaming knowledge is scattered: Arch Wiki, Valve repos, ProtonDB, distro docs, Discord servers. Several of those sources block automated fetchers. This skill distills all of it into one self-contained package an agent can load offline, route by symptom, and apply with appropriate caution.

`★ Insight ─────────────────────────────────────`
Most "gaming mode broken" bugs reduce to one mental model:
device → single-owner privilege → arbiter → unexpected second claimant.
Gamescope needs exclusive DRM master on the GPU. A lingering ghost
session, a leaked WAYLAND_DISPLAY, a compositor that didn't let go —
all the same bug wearing different clothes. The skill teaches the
pattern once, then maps every variant to it.
`─────────────────────────────────────────────────`

## What it covers

- **Session architecture** — gamescope embedded/nested modes, distro session stacks, systemd target wiring, Steam Linux Runtime (scout→steamrt4), the seven recurring failure patterns
- **Steam client** — install, runtime/library error tables, Flatpak Steam differences, NTFS, Remote Play
- **Proton & Wine** — launch options, prefixes, winetricks, DLL overrides, in-game launcher (EA/Ubisoft/Rockstar) patterns
- **Anti-cheat** — what works (EAC/BattlEye opt-in), what never will (kernel-level), cloud-gaming escape hatch
- **GPU** — AMD (module params, power sysfs, known hardware bugs) and NVIDIA (driver choice, version-match rule, Secure Boot, suspend VRAM, Xid errors), hybrid laptops
- **Input** — controller drivers per pad, udev rules, the double-input bug, Steam Input, SDL mappings
- **Audio** — PipeWire/WirePlumber architecture, failure table, ALSA fallback
- **Performance** — GameMode, MangoHud, CPU governors, shader pre-compilation, OOM/zram, split-lock stutter, recording
- **Display** — HDR per Proton variant, VRR, raytracing, Wayland color management
- **Steam Deck** — hardware IDs, firmware shortcuts, OLED audio on plain Arch

## How it works

```
SKILL.md          triage protocol + symptom routing + fix tiers
reference/        11 domain files, loaded on demand per symptom
scripts/          read-only diagnostic collectors (POSIX sh)
```

Triage-first design: the agent asks intake questions before touching anything (distro? GPU? gaming or desktop mode? what changed?), routes via symptom table, and labels every fix with a risk tier before running it.

**Fix tiers:** ✅ official → ⚠️ community-documented → 🟣 tribal (anecdotal, provenance required) → 🔴 deep/risky. Escalation in that order; 🔴 always needs explicit user confirmation.

`★ Insight ─────────────────────────────────────`
The 🟣 tribal tier is deliberate: community fixes that work but lack
official documentation are knowledge, not noise — IF they carry
provenance (source, date, confirmation count, reversal steps).
An unsourced fix is a rumor. Dated entries also self-prune:
on a rolling release, two-year-old tribal knowledge is suspect
by default.
`─────────────────────────────────────────────────`

## Diagnostic scripts

Three evidence collectors. Read-only, POSIX sh, degrade gracefully when tools are missing, locale-pinned output:

| Script | Collects |
|--------|----------|
| `diagnose-session.sh` | logind sessions, linger state, DRM holders, gamescope target state, journal failure signatures |
| `gpu-info.sh` | PCI/driver binding, Vulkan devices, AMD sysfs clocks/VRAM/thermals, kernel GPU errors |
| `audio-snapshot.sh` | audio server identity, PipeWire service state, sinks/sources, ALSA cards, bridge packages |

One script run replaces 15 manual commands and gives the agent a structured snapshot to reason over.

`★ Insight ─────────────────────────────────────`
Knowledge goes in markdown, procedure goes in scripts. Triage
questions need judgment — they stay prose. Evidence collection is
identical every time — it became a script. The script body never
enters the agent's context; only its output does.
`─────────────────────────────────────────────────`

## Install

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/steam-debugger
```

Full marketplace: [TuxLux40/skills](https://github.com/TuxLux40/skills)

## Sources

Distilled from ~25 Arch Wiki pages (Steam, Gamescope, AMDGPU, NVIDIA, Gamepad, PipeWire, Wine, HDR …), Valve's gamescope/steam-runtime/Proton repos, the Flathub Steam wiki, ProtonDB guides, distro docs, kernel.org GPU docs. Full list with per-source agent-access methods (some sites block plain fetchers): [`reference/sources.md`](reference/sources.md).

## License

CC-BY-SA 4.0 — substantial portions derive from the [Arch Wiki](https://wiki.archlinux.org) (CC-BY-SA).
