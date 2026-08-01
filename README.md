# skills

Agent skills by [TuxLux40](https://github.com/TuxLux40) — one marketplace for Claude Code, Grok, Cursor, Codex, and any harness that speaks [Agent Skills](https://agentskills.io).

## Skills

| Path | What it does |
|------|----------------|
| [`dokumenten-organisation`](skills/dokumenten-organisation) | Organize, name, and classify files for retrieval |
| [`kde-theming`](skills/kde-theming) | KDE Plasma themes (styles, Aurorae, plasmoids, KWin) |
| [`linux-tuner`](skills/linux-tuner) | Linux desktop performance (kernel, scheduler, VA-API, power) |
| [`smart-okf`](skills/smart-okf) | Local document knowledge base (ingest + retrieval) |
| [`steam-debugger`](skills/steam-debugger) | Steam on Linux (gamescope, Proton, GPU, audio) |
| [`stow`](skills/stow) | GNU Stow / dotfiles |
| [`usb-peripheral-debugger`](skills/usb-peripheral-debugger) | USB HID ownership, RGB daemons, reverse engineering |
| [`windows-styling-guide`](skills/windows-styling-guide) | Windows 11 Fluent → KDE Plasma |
| [`yubikey`](skills/yubikey) | YubiKey on Linux (PAM, FIDO2, PIV, …) |

Each skill folder has its own `README.md` with a one-line install.

## Install all (marketplace)

```bash
# Claude Code
claude plugin marketplace add TuxLux40/skills
claude plugin install tuxlux-skills

# Grok
grok plugin marketplace add TuxLux40/skills
grok plugin install TuxLux40/skills --trust
```

## Install one skill

```bash
# set NAME to e.g. steam-debugger, smart-okf, dokumenten-organisation
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/NAME
```

Swap `~/.claude/skills` for `~/.agents/skills`, `~/.copilot/skills`, etc. as needed.

## Layout

```
.claude-plugin/   Claude Code marketplace + plugin
.cursor-plugin/   Cursor
.codex-plugin/    Codex
.grok-plugin/     Grok
skills/           one directory per skill (SKILL.md + assets)
```

## License

MIT — see [LICENSE](LICENSE). Individual skills may note additional terms in their own files (e.g. CC-BY-SA for Arch Wiki–derived steam-debugger docs).
