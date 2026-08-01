# dokumenten-organisation

Agent-Skill zum **Ordnen, Benennen und Erschließen** von Dateien und Dokumenten — mit Methodik aus Archiv-, Bibliotheks- und Dokumentationswissenschaft.

Geeignet für [Claude Code](https://claude.com/claude-code) und andere Agenten im [Agent-Skills](https://agentskills.io)-Format. Die Referenzdateien sind reines Markdown und auch ohne Agent lesbar.

## Wofür

- chaotische Downloads-Ordner und unstrukturierte Dateisammlungen
- einheitliche **Dateinamens-Konventionen**
- **Ordnerstrukturen** / Aktenplan-ähnliche Klassifikation
- Verschlagwortung, Auffindbarkeit, Suchstrategien
- Aufbewahrung vs. Aussondern (Kassation)
- Vorbereitung für ein Dokumentenmanagement-System (DMS)

## Aufbau

```
SKILL.md              Anleitung und Arbeitsablauf
references/           Fachliche Vertiefung (bei Bedarf laden)
  aktenplan-und-klassifikation.md
  benennungskonventionen.md
  retrieval-und-suche.md
  aufbewahrung-und-kassation.md
  spezialbestaende.md
scripts/
  inventory.py        Nur-Lese-Inventur eines Verzeichnisses
```

## Arbeitsablauf (kurz)

1. **Inventur** — Bestand erfassen, nicht blind sortieren  
2. **Struktur** — Kategorien aus dem realen Bestand ableiten und abstimmen  
3. **Benennen** — z. B. `JJJJ-MM-TT--Thema_in_Snake_Case.endung`  
4. **Auffindbarkeit** — Navigation *und* Suche prüfen  
5. **Aussondern** — Duplikate/Altlasten bewusst bewerten, nicht blind löschen  

```bash
python3 scripts/inventory.py /pfad/zum/ordner
python3 scripts/inventory.py /pfad/zum/ordner --json
```

## Installation

Skill-Ordner in das Skills-Verzeichnis deines Agenten legen, z. B.:

```bash
git clone https://github.com/TuxLux40/dokumenten-organisation-skill.git \
  ~/.claude/skills/dokumenten-organisation
```

Oder den Inhalt von `SKILL.md`, `references/` und `scripts/` manuell nach `~/.claude/skills/dokumenten-organisation/` kopieren.

## Hinweis zum Umfang

Dieses Repository enthält **nur den Skill** (Anleitung, Referenzen, Inventur-Skript). Keine Kursunterlagen, keine PDF-Sammlungen, keine personenbezogenen Beispieldaten.

## Lizenz

MIT — siehe [LICENSE](LICENSE).
