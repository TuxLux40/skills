# skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-0A7EA4)](https://agentskills.io)

Agent skills by [TuxLux40](https://github.com/TuxLux40). One repo you can add as a marketplace in **Claude Code**, **Grok**, **Cursor**, **Codex**, **Hermes**, and any other harness that understands the [Agent Skills](https://agentskills.io) layout.

## Quick start

```bash
# Claude Code
claude plugin marketplace add TuxLux40/skills
claude plugin install tuxlux-skills

# Grok
grok plugin marketplace add TuxLux40/skills
grok plugin install TuxLux40/skills --trust

# Hermes (nousresearch.com/hermes-agent)
hermes skills tap add TuxLux40/skills
hermes skills install TuxLux40/skills/skills/NAME   # e.g. steam-debugger
```

## Skills

| Skill | Description |
|-------|-------------|
| [dokumenten-organisation](skills/dokumenten-organisation) | Organize, name, and classify files so they stay findable |
| [flipper-zero](skills/flipper-zero) | Flipper Zero — qFlipper connection fixes, deploy workflow, Momentum GUI dev |
| [kde-theming](skills/kde-theming) | KDE Plasma themes — styles, Aurorae, plasmoids, KWin effects |
| [linux-tuner](skills/linux-tuner) | Desktop performance — kernel, scheduler, VA-API, power stack |
| [smart-okf](skills/smart-okf) | Local-first document knowledge base (ingest + retrieval) |
| [steam-debugger](skills/steam-debugger) | Steam on Linux — gamescope, Proton, GPU, audio, sessions |
| [stow](skills/stow) | GNU Stow — dotfiles, package trees, conflict recovery |
| [usb-peripheral-debugger](skills/usb-peripheral-debugger) | USB HID ownership, RGB daemons, reverse engineering |
| [windows-styling-guide](skills/windows-styling-guide) | Windows 11 Fluent design tokens mapped to KDE Plasma |
| [yubikey](skills/yubikey) | YubiKey on Linux — PAM, FIDO2, PIV, OpenPGP, OATH |

Each skill ships with `SKILL.md` plus references/scripts as needed. See the skill’s own `README.md` for a one-line install.

## Install a single skill

```bash
# NAME = folder under skills/, e.g. steam-debugger
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz \
  | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/NAME
```

Use `~/.agents/skills`, `~/.copilot/skills`, or a project-local `.claude/skills` if that matches your agent.

## Repository layout

```
.claude-plugin/   Claude Code marketplace + plugin manifest
.cursor-plugin/   Cursor
.codex-plugin/    Codex
.grok-plugin/     Grok
skills.sh.json    Category groupings for Hermes Skills Hub / skills.sh
skills/           one directory per skill
```

## License

[MIT](LICENSE). Some skills note extra terms in their tree (e.g. CC-BY-SA where Arch Wiki material is used).
