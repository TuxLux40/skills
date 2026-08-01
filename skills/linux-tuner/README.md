# linux-kernel-tuner

A Claude Code skill for Linux desktop performance tuning.

## What it does

Covers two layers:

1. **Kernel + scheduler** — which kernel, which scheduler (BORE, EEVDF, sched_ext), power stack
2. **Desktop snappiness** — VA-API video decode, browser hardware acceleration, preload, KDE cgroup boosters, sysctl tweaks

Works in CLI mode (runs diagnostics itself) and web UI mode (asks only for missing facts). Generates a **runnable bundle** (`linux-tune/apply-all.sh`) in CLI mode so you can review and run changes in one shot with full rollback.

## Covers

- Schedulers: BORE, EEVDF, BMQ/PDS, sched_ext (scx_lavd, scx_rusty, scx_layered, scx_bpfland)
- Kernels: CachyOS, Xanmod, Liquorix, linux-zen, -rt, stock/LTS
- Power: TLP, auto-cpufreq, tuned, power-profiles-daemon — conflict detection + correct config
- VA-API: Intel iHD vs i965 matrix, AMD, verification
- Browser HW accel: Chromium-based flags + config file paths, Wayland-only guard
- KDE boosters: plasma-foreground-booster, dmemcg-booster (AUR/Arch only)
- Distros: Arch, CachyOS, Fedora, Ubuntu/Debian, openSUSE, NixOS, Gentoo

## Install (nur dieser Skill)

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/linux-tuner
```

Oder lokal aus diesem Ordner:

```bash
mkdir -p ~/.claude/skills && cp -r . ~/.claude/skills/linux-tuner
```

## Alle Skills (Marketplace)

```bash
# Claude:  claude plugin marketplace add TuxLux40/skills && claude plugin install tuxlux-skills
# Grok:    grok plugin marketplace add TuxLux40/skills && grok plugin install TuxLux40/skills --trust
```

Quelle: [TuxLux40/skills](https://github.com/TuxLux40/skills)

## References

Self-contained reference files in `references/`:

| File | Contents |
|------|----------|
| `schedulers.md` | scx use cases, BPF requirements, scxctl, decision matrix |
| `kernels.md` | CachyOS variants + repo setup, Xanmod, Liquorix, Fedora COPR, NixOS |
| `vaapi.md` | Driver matrix, install by distro, browser flags |
| `power.md` | TLP/auto-cpufreq/tuned/PPD conflict matrix, config syntax |
| `desktop-snappiness.md` | preload, KDE boosters, zram, THP, I/O scheduler |
| `sysctl.md` | vm params, BBR, CPU isolation, tuned profiles, diagnostics |
