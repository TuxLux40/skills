# genealogy

Bilingual (DE/EN) genealogy research skill focused on Germany: Genealogical Proof Standard + Quellenkritik, fact-level citations, research log, and a strict verification protocol for MyHeritage Smart Matches and other tree hints to keep false positives out of the tree.

Zweisprachiger Ahnenforschungs-Skill: wissenschaftliche Methodik, saubere Quellenangaben, Forschungsprotokoll und ein strenges Prüfverfahren für MyHeritage Smart Matches.

## Install

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/genealogy
```

## Contents

| Path | Purpose |
|------|---------|
| `SKILL.md` | Principles, status vocabulary, workflow, routing to references |
| `references/smart-match-pruefung.md` | Match verification protocol, verdict format, false-positive patterns |
| `references/methodik-gps-quellenkritik.md` | GPS, evidence analysis, source criticism, conflict resolution |
| `references/quellen-deutschland.md` | Record types, archives, portals, access rules |
| `references/regionale-besonderheiten.md` | Names, calendars, territories, confession, script |
| `references/zitieren-und-dokumentation.md` | Citation format, fact-level sourcing, research log, publishing |
| `references/ablage-und-erschliessung.md` | Filing and cataloguing: provenance, file names, person and place register, controlled tags, Findbuch, photos |
| `references/region-nrw-rheinland.md` | Rhineland, Ruhr area, Essen, Mülheim an der Ruhr |
| `references/land-niederlande.md` | Netherlands — short reference |
| `references/land-ungarn.md` | Hungary — short reference |
| `references/dna-myheritage.md` | DNA basics with MyHeritage's tools |
| `references/archive-und-anfragen.md` | Core list of archives, request workflow and tracking |
| `references/interview-oral-history.md` | Interviews with relatives: guide, transcription, evaluation |
| `references/erweiterte-recherche.md` | Advanced tactics: events abroad, cluster search, finding relatives |
| `references/schnittstellen-katalog.md` | APIs, exports and open standards, with evidence value |
| `references/ausgabeform.md` | Output shape: verdict first, one next step, and what brevity never removes |
| `references/faecher-modus.md` | Divergent mode for dead ends: isolated branches, genealogy frame pack, leads as testable predictions |
| `references/notizen-okf.md` | Notes as OKF Markdown: note types, frontmatter, link rules, Obsidian graph setup |
| `references/glossar-de-en.md` | DE↔EN glossary, register Latin, abbreviations |
| `assets/vorlagen.md` | Templates in German and English |
| `scripts/gedcom_plausi.py` | Read-only GEDCOM plausibility check (stdlib) |
| `scripts/okf_check.py` | Read-only check of the notes: OKF conformance, link rules, unchecked readings (stdlib) |
| `evals/` | Scenario prompts, a test GEDCOM, and an example note bundle that opens as an Obsidian vault (`fixtures/okf-beispiel/`) |

```bash
python3 scripts/gedcom_plausi.py tree.ged --lang de        # or --lang en, --json
python3 scripts/okf_check.py path/to/notes --lang de       # or --lang en, --json
```

## Works with

- [`dokumenten-organisation`](../dokumenten-organisation) — the general method for filing plan, naming, retrieval and appraisal; `references/ablage-und-erschliessung.md` applies it to a genealogy project and uses its file-name pattern and inventory script.

## Credits

Three modes adapt methods from other skills, re-expressed for genealogical research (all MIT):

- **Ausgabeform** — [i-have-adhd](https://github.com/ayghri/i-have-adhd) © 2026 Ayoub Ghriss
- **Fächer-Modus** — [ADHD — a skill for agents](https://github.com/UditAkhourii/adhd) © 2026 ADHD contributors
- **Grill-Modus** — [grill-me](https://github.com/mattpocock/skills) © 2026 Matt Pocock

Full marketplace: [TuxLux40/skills](https://github.com/TuxLux40/skills) · details in `SKILL.md`
