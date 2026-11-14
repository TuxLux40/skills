# ahnenforschung

Bilingual (DE/EN) genealogy research skill focused on Germany: Genealogical Proof Standard + Quellenkritik, fact-level citations, research log, and a strict verification protocol for MyHeritage Smart Matches and other tree hints to keep false positives out of the tree.

Zweisprachiger Ahnenforschungs-Skill: wissenschaftliche Methodik, saubere Quellenangaben, Forschungsprotokoll und ein strenges Prüfverfahren für MyHeritage Smart Matches.

## Install

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/ahnenforschung
```

## Contents

| Path | Purpose |
|------|---------|
| `SKILL.md` | Principles, status vocabulary, workflow, routing to references |
| `references/smart-match-pruefung.md` | Match verification protocol, verdict format, false-positive patterns |
| `references/methodik-gps-quellenkritik.md` | GPS, evidence analysis, source criticism, conflict resolution |
| `references/quellen-deutschland.md` | Record types, archives, portals, access rules |
| `references/regionale-besonderheiten.md` | Names, calendars, territories, confession, script |
| `references/zitieren-und-dokumentation.md` | Citation format, file naming, folder structure, research log |
| `references/glossar-de-en.md` | DE↔EN glossary, register Latin, abbreviations |
| `assets/vorlagen.md` | Templates in German and English |
| `scripts/gedcom_plausi.py` | Read-only GEDCOM plausibility check (stdlib) |
| `evals/` | Scenario prompts and a test GEDCOM |

```bash
python3 scripts/gedcom_plausi.py tree.ged --lang de        # or --lang en, --json
```

Full marketplace: [TuxLux40/skills](https://github.com/TuxLux40/skills) · details in `SKILL.md`
