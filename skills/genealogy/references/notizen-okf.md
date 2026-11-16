# Notizen als OKF-Markdown / Notes as OKF Markdown (Obsidian-ready)

Every note this skill writes — person profile, family group, source sheet
with transcription, hypothesis, research log — is a Markdown file with YAML
frontmatter in the Open Knowledge Format (OKF v0.2). Plain files: readable
anywhere, diffable, bound to no tool. Obsidian opens the folder as a vault
and draws the notes as a graph.

A graph is drawn from links. So the core of this file is §3, **what may be
linked to what**: a line in the graph must not show more than the evidence
does.

## 1. Notiztypen / Note types

| `type` | One note per | File name | Body template (`assets/vorlagen.md`) |
|--------|--------------|-----------|--------------------------------------|
| `Person` | individual | `P0042_MUSTER-Johann-Heinrich_1788.md` | §18 |
| `Family` | couple with their children — the link between persons | `F0012_MUSTER-BEISPIEL_1815.md` | §18 |
| `Place` | place, with parishes and offices over time | `Beispieldorf.md` | §18 |
| `Source` | record or document: citation, image, transcription, extraction | base name of the scan + `.md` | §2, §8, §17 |
| `Hypothesis` | anything below *wahrscheinlich*: unproven link, candidate identity, rejected match, override | `H0007_<Kurztitel>.md` | §3 |
| `Proof` | proof argument, conflict analysis | `B0003_<Kurztitel>.md` | §4, §5 |
| `ResearchLog` | research question; divergent run; person network | `<JJJJ-MM-TT>--<Frage>.md` | §1, §13, §14 |
| `Session` | session summary | `<JJJJ-MM-TT>--Sitzung.md` | §12 |
| `Register` | list: Findbuch, tag list, request tracking | by content | §9, §15, §16 |

`type` is a free string in OKF; these nine are the skill's vocabulary. Notes
of other types in the same folder belong to other tools and are left alone.

## 2. Frontmatter

```yaml
---
type: Person                        # the one field OKF requires
id: P0042
title: "MUSTER, Johann Heinrich (*1788 Beispieldorf)"
description: Getauft 1788 in Beispieldorf; Sohn von Peter Muster und Anna Maria Beispiel.
aliases:                            # every name form found in sources
  - Johann Heinrich Muster
  - Joes Henricus Muster
tags:
  - familie/Muster
  - ort/Beispieldorf
conclusion: belegt                  # the skill's status vocabulary
status: stable                      # OKF lifecycle: draft | stable | deprecated
generated: { by: <agent>/<version>, at: 2026-11-14T18:40:00Z }
verified: { by: human:<id>, at: 2026-11-15T09:00:00Z }   # only after a human check
---
```

| Type | Fields besides `type`, `title`, `description`, `tags`, `status`, `generated` |
|------|------------------------------------------------------------------------------|
| Person | `id`, `aliases`, `conclusion`, `sex`, `kekule`, `gedcom_xref`, `myheritage_id`, `familysearch_id` |
| Family | `id`, `conclusion`, `gedcom_xref` |
| Place | `aliases` (historical names), `gov_id` |
| Source | `record_type`, `record_date`, `repository`, `call_number`, `locator`, `source_class` (Original, Derivat, Kompilation, Index), `seen_as` (Original, Digitalisat, Kopie, Index), `seen_at`, `resource` (permalink), `file` (the master), `sha256`, `original_filename`, `script`, `language`, `terms_of_use`, `verified` |
| Hypothesis, Proof | `id`, `conclusion` |

Three fields that answer three different questions:

| Field | Question | Values |
|-------|----------|--------|
| `conclusion` | How well is this established? | belegt · wahrscheinlich · möglich · ungeklärt · widerlegt — and `ungeprüft` for what was taken over from the tree and not evaluated yet |
| `status` | Is the note itself finished? | draft · stable · deprecated |
| `verified` | Has a human checked the content against its source? | one or more `{ by, at }` |

- **`verified` on a Source note means: the transcription was checked at the
  image.** No entry by a `human:` actor = "maschinell gelesen, ungeprüft".
  You never write a `human:` verification on your own; you add it when the
  user says they have checked, with that date.
- `generated.by` is `<agent>/<version>` for a model and `human:<id>` when the
  user wrote the note; `generated.at` is the last change of substance.
- `deprecated` marks a note that was merged or replaced: keep it, with one
  line saying where its content went. A disproven hypothesis is not
  deprecated — it is `conclusion: widerlegt` and stays.
- Keep the frontmatter flat apart from `generated` and `verified`; Obsidian
  shows nested values only in source mode.
- Optional `stale_after` for what expires: a negative search in a collection
  that is still growing, a request waiting for an answer.

## 3. Ein Link ist eine Behauptung / A link is a claim

**Form.** Standard Markdown links with a relative path and the `.md`
extension; the link text is the register form of the target:

```markdown
[MUSTER, Johann Heinrich (*1788 Beispieldorf)](../20_personen/P0042_MUSTER-Johann-Heinrich_1788.md)
```

No wikilinks, no block references, no paths starting with `/`. A relative
link means the same to OKF, Obsidian, GitHub and a file browser.

**Meaning.**

| From → to | Says | Allowed when |
|-----------|------|--------------|
| Person ↔ Family | kinship | *belegt* or *wahrscheinlich*, the status written beside the link — or *ungeprüft* where the note mirrors what the master tree already asserts (§6) |
| Person, Family → Source | this fact rests on this record | always; the status stands in the same row |
| Source → Person | "the one named here is this person" — an identity claim | identity *belegt* or *wahrscheinlich*, **and** the reading checked where the record is handwritten; otherwise the name stays text |
| any → Place | where | always |
| Hypothesis → Person, Source | "is about" | always — this is where the weaker links live |
| any → Hypothesis | "open question here" | always |
| ResearchLog, Session, Register → any | working context | always |
| Person → Person | — | **never.** Kinship runs through a Family note; "nicht identisch mit" is text with the ID |

Why this strict: an edge in a graph has no label and no status. Two person
nodes joined by a line read as "related", whatever the note says. The
Family note in between makes kinship visible as kinship; the Hypothesis note
in between makes a guess visible as a guess. Filter the hypothesis notes
out, and what remains is the tree; colour the notes by `conclusion`, and it
shows how far that tree is proven.

People who are only named in a record — godparents, witnesses — get a note
of their own when they are in scope or turn up a second time. Until then
they stay text in the extraction table. Linking two mentions to one note is
the claim that it is one person.

## 4. IDs und Dateinamen / IDs and file names

- **Use the IDs the project already has** — a person register, the IDs in
  existing file names (`SCH-IRI`, `FAM-SCH-ERN`), the IDs of the tree
  software. An ID is an opaque token: unique, assigned once, never reused.
  Only where none exist: `P`, `F`, `H`, `B` plus four digits.
- An ID built from name parts collides as soon as a namesake appears, and
  namesakes are the rule in this field. The register decides the second ID
  before the first file is named; a suffix is enough (`MUS-JOH-2`).
- The ID stands in the file name as its own token: a broken link can be
  repaired from it, files can be gathered by it (§6), and the rest keeps the
  name readable — Obsidian labels graph nodes with the file name, not with
  `title`.
- Person: `<ID>_<NACHNAME>-<Vorname>_<Geburtsjahr>`; estimated year as
  estimated, unknown `0000`.
- Rename (a corrected birth year) inside Obsidian with link updating on, or
  in one scripted pass that rewrites the links.
- A Source note sits beside the file it describes and shares its base name.
- `index.md` and `log.md` are reserved by OKF at every level; never name a
  note that way. A bundle-root `index.md` may declare `okf_version: "0.2"`.
  A per-folder `index.md` — a list of links with descriptions, no
  frontmatter — is the generated form of a register.

## 5. Schlagwörter und Namensformen / Tags and aliases

- `tags`: the controlled list (`ablage-und-erschliessung.md` §6) as nested
  tags — `familie/Muster`, `ort/Beispieldorf`, `quelle/Taufe`,
  `lesung/maschinell-ungeprüft`. No spaces.
- **Persons are linked, never tagged.** A tag is an identity claim without a
  status.
- `aliases` on a Person note hold every name form found in the sources. The
  note is then found under each of them, and Obsidian's backlinks pane lists
  the *unlinked mentions*: every plain-text occurrence of an alias in other
  notes. Those are candidates for the connection scan (`faecher-modus.md`
  §6), not identifications.
- With `title` and `aliases` the person note *is* its register row. A
  register table is then a generated listing, not a second place to keep
  up to date.

## 6. Baum-Spiegel und Dokumenten-Index / Tree mirror and document index

One note per person and per family, holding what the tree holds — vital
data, relationships, citations, notes — plus what a tree cannot hold: proof
status, links to source notes, open questions, the files that belong to the
person. **The tree data is copied by script, never retyped by you**: a model
that retypes two hundred dates gets some of them wrong, and nobody sees
which.

```bash
python3 scripts/gedcom_to_okf.py tree.ged --list-ids            # xref;name;born;died
python3 scripts/gedcom_to_okf.py tree.ged --root <root> \
    --persons-dir <dir> --families-dir <dir> --id-map ids.csv     # dry run
python3 scripts/gedcom_to_okf.py tree.ged --root <root> … --write
python3 scripts/gedcom_to_okf.py neuer-export.ged --root <root> … --update --write
python3 scripts/okf_docindex.py <root> --notes <dir> --write
```

- **IDs.** `--id-map` is a list `xref;id` that ties the tree's records to
  the project's own IDs. Without it the GEDCOM cross-reference is the ID.
  Settle the IDs before the first `--write`.
- **What is generated** lies between `<!-- BEGIN gedcom -->` and `<!-- END
  gedcom -->`. `--update` replaces that block and nothing else: frontmatter
  — including a `conclusion` set after review — and every section below the
  block stay untouched. A note without the markers is never touched.
- **Status.** A fact carries the status found as a prefix in its citation or
  note in the tree (`[belegt]` …). Without one it is `ungeprüft`: taken
  over, not evaluated. New notes start with `conclusion: ungeprüft`; you
  raise it only after the evidence has been worked through, and then in the
  tree as well.
- **Corrections go into the tree**, not into the block. The next export
  brings them back.
- **Document index.** `okf_docindex.py` lists, in each note, the files whose
  names carry the note's ID as a token (`1964-06-09_SCH-IRI_GBUR.pdf`),
  between `<!-- BEGIN dokumente -->` and `<!-- END dokumente -->`. It shows
  how files were filed. That a file bears a person's ID is an assignment
  made when filing, not evidence; what a document proves is said in a Source
  note.
- Both scripts run dry unless `--write` is given, and report every file
  they would touch.

## 7. Obsidian

Open the bundle root as a vault. Three settings keep the files portable
(Settings → Files and links): **Use [[Wikilinks]]** off · **New link
format** "Relative path to file" · **Automatically update internal links**
on. And Settings → Editor → **Properties in document** "Source", so nested
frontmatter is shown as written.

Graph view, colour groups — each group is a search query:

| Group | Query |
|-------|-------|
| Not yet evaluated | `[conclusion:ungeprüft]` |
| Persons | `[type:Person] -[conclusion:ungeprüft]` |
| Families | `[type:Family] -[conclusion:ungeprüft]` |
| Sources | `[type:Source]` |
| Places | `[type:Place]` |
| Hypotheses | `[type:Hypothesis]` |
| Proofs | `[type:Proof]` |
| Working notes | `[type:ResearchLog] OR [type:Session] OR [type:Register]` |

Views, typed into the graph's filter:

| View | Filter |
|------|--------|
| The tree | `[type:Person] OR [type:Family]` |
| The tree with its evidence | `[type:Person] OR [type:Family] OR [type:Source]` |
| Readings still to check at the image | `[type:Source] -[verified]` |
| Open questions | `[type:Hypothesis] OR [conclusion:möglich] OR [conclusion:ungeklärt]` |
| The tree as far as it is evaluated | `([type:Person] OR [type:Family]) -[conclusion:ungeprüft]` |

- Local graph of a person at depth 2: the family group with its records.
  Depth 3 adds everyone named in the same records — the cluster.
- "Existing files only" off shows notes that are linked but not written.
- "Tags" on turns `familie/…` and `ort/…` into hubs.
- A preset with these settings and groups lies in the example bundle
  (`evals/fixtures/okf-beispiel/.obsidian/`): copy `app.json` and
  `graph.json` into the vault's `.obsidian/` folder while Obsidian is
  closed — it rewrites both files when it quits.

The graph shows what is linked, not what is true. It is a view of the notes;
the master tree stays where the working setup says it is.

## 8. Prüfen / Checking

```bash
python3 scripts/okf_check.py <bundle-root> [--lang de|en] [--json]
```

Read-only. Reports notes without `type`, duplicate IDs, unknown `conclusion`
values, a proof status written into `status`, wikilinks and absolute links,
missing link targets, person-to-person links, persons or families below
*wahrscheinlich*, person links out of an unchecked reading of handwriting,
and lines that say "belegt" while citing a reading nobody has checked. Run
it after each batch of new notes. Clean means consistent, not correct. The
summary counts persons and families by `conclusion` — how much of the tree
is evaluated, and how much is still `ungeprüft`.

## 9. Beispiel / Example

`evals/fixtures/okf-beispiel/` — twelve notes with invented data: a proven
baptism, a namesake known only from an index, and a marriage entry whose
unchecked reading keeps the marriage in a hypothesis note instead of the
tree. Copy the folder before opening it as a vault; Obsidian writes its own
files into it.

## Grundlagen / Basis

- Open Knowledge Format v0.2:
  <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>
  — `type` required; `generated`, `verified`, `status`, `sources` optional;
  links are plain Markdown; `index.md` and `log.md` reserved.
- Obsidian help on internal links, properties, search and graph view:
  <https://help.obsidian.md>
