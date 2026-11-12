# ifixit

Hardware repair via the iFixit API: resolve the exact device, pull guides/tools/parts, produce a safety-first repair plan with a marked point of no return. Stdlib-only CLI included (`scripts/ifixit.py`).

## Install

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/ifixit
```

## CLI

```bash
python3 scripts/ifixit.py suggest "thinkcentre"
python3 scripts/ifixit.py search "pixel 8 battery"
python3 scripts/ifixit.py device "Google Pixel 8"
python3 scripts/ifixit.py guide 166180 --lang de
```

Full marketplace: [TuxLux40/skills](https://github.com/TuxLux40/skills) · details in `SKILL.md`
