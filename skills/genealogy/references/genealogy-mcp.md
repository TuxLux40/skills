# genealogy-mcp (optional MCP server)

Third-party MCP server by igormel81 (MIT, PyPI `genealogy-mcp`, source
github.com/igormel81/genealogy-mcp). Described here from its listing and a
static read of release 0.7.0 — it was **not executed** while writing this
file, so treat tool behaviour as documented-by-author until seen in use, and
re-check the tool list when the server is connected (versions change).

## Setup

```json
{ "mcpServers": { "genealogy": { "command": "uvx", "args": ["genealogy-mcp"] } } }
```

No API key. If its tools (`mcp__genealogy__*` or similar) are not present in
the session, say so and continue with the skill's own references — never
pretend a tool ran.

## How it fits this skill

The server supplies **calculators, catalogues and bookkeeping**; this skill
supplies the **standard of proof**. Where the two differ, this skill's rules
win.

| Workflow step (SKILL.md) | Tool | Use | Caveat |
|---|---|---|---|
| 3 Plan | `plan_research`, `find_sources`, `source_details`, `record_guide` | First pass on which records exist for a country/period | Catalogue has 171 sources with a Russian-Empire / Eastern-Europe centre of gravity; for Germany it knows Archion, Matricula, GenWiki/CompGen, GEDBAS, Online-OFB, Verlustlisten, DDB, Bundesarchiv, Arolsen, Volksbund — but not Meyers Gazetteer, state-archive portals or Ancestry. Complete the plan from `quellen-deutschland.md` |
| 3 Place | `place_history`, `where_are_records` | Affiliation of a place over time (Wikidata); which archive now holds a former province's records — strongest for East Prussia, Posen, Galicia, Baltics, Russian Empire | Wikidata is a compiled source: confirm against GOV / Meyers before citing |
| 4 Search | `search_links`, `search_online`, `search_book_pages` | Ready search URLs for name variants; live search of Internet Archive, Chronicling America, WikiTree, Open Archives, Open List, Gallica | Sends the queried names to those services — never for living persons. Hits are index/OCR/tree leads; fetch the image. A 403/503 or login wall is "not checked", not "not found" |
| 5 Capture | `normalize_date`, `convert_calendar`, `feast_date`, `birth_year_from_age`, `cyrillic_numerals`, `glossary` | Julian↔Gregorian, French Republican, Hebrew dates; feast-day dates; age → birth-year range | Keep the date as written in the transcription; put the conversion beside it. Feast and glossary data are oriented to Orthodox/Russian usage — for Western feasts check Grotefend |
| 6 Analyse | `name_variants`, `estimate_birth_year`, `kinship`, `dna_match` | Spelling/transliteration variants and Daitch–Mokotoff codes; estimated birth year from relatives; relationship ranges for shared cM | Estimates are entered as `EST`/`BET…AND` with the derivation, never as facts. DNA ranges suggest relationships; documents prove them |
| Match protocol | `check_match` | Fact-by-fact comparison of "known" vs "found" | Its `confirmed` means two independent facts beyond the name. That is **below** this skill's threshold (≥ 3 identifiers incl. a relationship, namesake search, original record seen). Use its comparison to fill the matrix; its verdict can lower ours (`conflict`, `different_person` → investigate), never raise it |
| Match protocol | `parent_hypothesis` | Ranks candidate fathers from a patronymic | Useful in patronymic regions (Ostfriesland, Schleswig, Eastern Europe). Output is a hypothesis → `40_hypothesen/`, status at most *möglich* |
| 8 / QA | `audit_tree`, `project_evidence`, `project_coverage`, `film_reading_plan` | Tree audit (GEDCOM), per-event citation coverage, which register volumes/frames were read | Run alongside `scripts/gedcom_plausi.py`; the two use different rules, review both lists |
| 7 Letters | `draft_archive_request` | Draft request letter | A draft for the user to check and send; compare with the German template in `assets/vorlagen.md` |
| Log | `project_view`, `project_save`, `project_log`, `project_policy`, `project_transfer` | Persistent project: sources, people, leads, searches | **Write tools.** See below |

## Write tools — rules

`project_save`, `project_log` and the other write-annotated tools can change
a project folder, and when given a GEDCOM path they **edit that file in
place**.

1. Point them at a working copy, never at the only copy of the user's tree;
   make a dated GEDCOM backup first (`90_export/`).
2. Use the dry-run/preview, show the user the diff, and write only after an
   explicit yes for that change. A general "go ahead" earlier in the
   conversation does not cover a later merge or relationship edit.
3. Never let a tool write a relationship, merge or match result whose verdict
   under `smart-match-pruefung.md` is below *belegt*.
4. After writing, run `scripts/gedcom_plausi.py --json` before and after and
   diff the two reports.

If the user already keeps a research log in their own knowledge base, do not
start a second one in the server's project store without asking — one log.

## What it does not replace

- The Smart-Match protocol and verdict format.
- German-specific knowledge in `regionale-besonderheiten.md` (Rufname,
  Hofnamen, confession, territories) and the DE↔EN glossary.
- Reading the original record.
