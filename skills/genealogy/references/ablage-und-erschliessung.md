# Ablage und Erschließung / Filing and cataloguing

Where files go, what they are called, and how they are found again. The
general method — filing plan, naming, retrieval, appraisal — is the sibling
skill `dokumenten-organisation`; this file applies it to a genealogy
project. Division of labour: `dokumenten-organisation` arranges files,
`smart-okf` reads them into a knowledge base, this skill says what they
prove.

**The user's existing structure and naming take precedence.** Everything
below is the fallback, and the standard for what is newly added.

## 1. Erst Inventur / Inventory first

- Do not make the user describe their storage if you can reach it. Take a
  read-only inventory (the sibling skill's
  `dokumenten-organisation/scripts/inventory.py <root>`, or `find`), state
  your reading of the structure in at most five lines and have it confirmed
  once. Note root path, top-level folders and naming habits in the research
  log.
- Derive categories from what is there. No empty folders for a hypothetical
  future; create a folder when its first file exists.
- Never reorganise an existing collection unasked. Propose, get the
  decision, then move or rename in **one scripted pass** and save the
  old → new map in the log. File names are cited; a silent rename breaks
  citations.

## 2. Provenienz zuerst / Provenance first

Sources are filed by where they come from (repository → Bestand → unit),
not by the person they mention: one register page names many people. The
person is the second way in (§6).

**Family papers have a provenance too** — the person or household that kept
them. Before anything is re-sorted, taken out of an album or scanned out of
sequence, record

- who holds it now, who held it before, where it was found;
- the **original order**: album and page sequence, bundles, envelopes, what
  lay next to what — as a list, or by scanning in sequence and keeping the
  scanner's file numbering in the sidecar;
- front **and back** of photos, postcards and certificates: inscriptions,
  stamps, studio imprints.

Neighbourhood is evidence: the photos on the same album page, the letter in
the envelope, the bundle a certificate was kept in. Dissolved into person
folders, it is gone. A relative's collection stays one unit under its
keeper's name; person notes link into it.

## 3. Ordnerstruktur / Folder structure (fallback)

```
genealogie/
  00_forschungsprotokoll/   research log, one file per question; session summaries
  05_register/              person and place register, tag list, Findbuch (§5, §6)
  10_quellen/               sources, by repository → Bestand → unit
    Familienarchiv/<Verwahrer>/   home sources, original order kept
    Literatur/              published works
  20_personen/              one note per person, ID in the file name
  30_familien-orte/         family-group and place notes
  40_hypothesen/            unproven links, rejected matches, overrides, divergent runs
  50_korrespondenz/
    ausgang/                your own requests and letters
    eingang/                replies — these are sources
  90_export/                dated GEDCOM backups, DNA exports
```

- Flat: three to four levels. Numbered prefixes with gaps keep the order
  stable when something is inserted later.
- One place per file; link, never duplicate.
- **Sources and your own writing never share a folder.** `10_quellen/` and
  `50_korrespondenz/eingang/` hold what others produced; logs, notes,
  hypotheses and outgoing letters hold what you or the user concluded.
  This is what lets an ingest pipeline index the sources without swallowing
  your conclusions (`dokumenten-wissensbasis.md` §7).
- One line per top-level folder in a README at the root — what belongs
  here, what does not — keeps the structure from eroding.

## 4. Dateinamen / File names

The house pattern of the sibling skill, `[Datum]--[Thema]__[Zusatz].[Endung]`,
filled in for genealogy:

```
<JJJJ-MM-TT>--<Ereignis>_<NACHNAME>-<Vorname>_<Ort>__<Herkunft>_<Fundstelle>[_<Zusatz>].<ext>

1788-03-14--Taufe_MUSTER-Johann-Heinrich_Beispieldorf__BAM-KB4_S112-Nr23.jpg
1891-05-16--Heirat_MUSTER-BEISPIEL_Musterstadt__StAM-HR1891_Nr204.pdf
1851-07-02--Taufe_MUSTER-Anna_Beispieldorf__Familienarchiv-Beispiel_Abschrift-1937.pdf
1925-00-00--Foto_MUSTER-Anna_Musterstadt__Album-Erna-Beispiel_S07-r.jpg
1925-00-00--Foto_MUSTER-Anna_Musterstadt__Album-Erna-Beispiel_S07-v.jpg
```

- **Datum** — the date of the event the record is about, ISO 8601, so the
  files of a person sort into a timeline. Unknown parts `00` / `0000`. A
  later copy keeps the event date in front and carries its own year in the
  Zusatz (`_Abschrift-1937`): an original and a copy made eighty years
  later must not look alike.
- **Thema** — event from a fixed list (Geburt, Taufe, Heirat, Tod,
  Begraebnis, Foto, Brief, Urkunde, Interview …), person in the form of the
  register (§5), place in its preferred form.
- **Zusatz** after `__` — where the file comes from (archive abbreviation
  and Signatur, or the keeper of family papers), the Fundstelle (`S`, `Bl`,
  `Nr`; `-r` / `-v` for front and back), then the suffix of a derivative
  (`_bearb`, `_ausschnitt`, `_transkript`).
- `-` inside an element, `_` between elements, `--` and `__` only between
  the three blocks. No spaces. Umlauts the way the storage already handles
  them — but always the same way.
- **One name, one spelling.** File names use the register form, never the
  spelling of the individual record; that belongs in the transcription.
  Two persons with the same name form: append the person ID
  (`MUSTER-Johann_P0042`).
- No meaningless names (`IMG_2384.jpg`, `scan0012.pdf`): look at the
  content before naming. The original file name goes into the sidecar — it
  preserves the scanning sequence.
- Published works: `NACHNAME_Vorname--Titel_JJJJ.pdf`. Saved web pages:
  `Web--<domain>_<Titel>`, moved together with their asset folder.
- Dated exports: `JJJJ-MM-TT--<Baum>.ged`.

Media: scans as TIFF/PNG or the JPEG as delivered; documents PDF/A; audio
WAV/FLAC as master; DNA exports as downloaded plus a dated copy. A NAS is
not a backup: keep a second copy elsewhere and test restoring it.

## 5. Ansetzung und Register / Authority forms and registers

The thesaurus principle applied to people and places: one preferred form,
every variant mapped to it. Templates: `assets/vorlagen.md` §15.

- **Personenregister** — one row per person: ID (`P0001`, stable and
  independent of any website) · Ansetzungsform `NACHNAME, Vorname(n) (*JJJJ
  Ort)` · variant names and spellings, each with the source it occurs in ·
  Kekulé number as an attribute (it shifts with the proband and does not
  cover siblings) · external IDs (MyHeritage, FamilySearch) · status of the
  identity.
- Year and place of birth — or of the earliest known event, marked `~` —
  belong to the form, because the bare name repeats in every generation.
- Two candidates of the same name are two rows from the first day, each
  with "nicht identisch mit P0xxx" once that is established. Never one row
  that quietly covers both.
- **Ortsregister** — one row per place: preferred name and GOV-ID ·
  historical names and spellings · parish(es), Standesamt and territory
  with the dates each applied · same-named places to rule out.
- The same form everywhere: file names (compact, `MUSTER-Johann-Heinrich`),
  tags, person notes, replies. Source spellings stay in the transcriptions
  and in the variant column — the register is where "Schmitz", "Schmits"
  and "Smeets" meet without being merged in the sources.
- The variant column is the search list: it feeds the variant matrix in
  `erweiterte-recherche.md` §3.

## 6. Zweiter Zugriffsweg / The second way in: links, tags, Findbuch

Every file must be reachable two ways — by walking the provenance tree, and
by searching for a person, place or record type. Filed by provenance alone,
a record is hidden from everyone it names.

- **Links.** The person note links to every source file for that person;
  the sidecar of a source lists the IDs of the persons it names. Relative
  links, so the tree of folders can move.
- **Kontrollierte Schlagwörter / controlled tags.** Fixed facets, fixed
  terms. A synonym is mapped to the term, not added as a tag — otherwise
  "Heiratsurkunde", "Eheurkunde" and "marriage certificate" split one
  search into three.

  | Facet | Term | Example |
  |-------|------|---------|
  | person | person ID | `P0042` |
  | familie | surname in register spelling | `Muster` |
  | ort | preferred place name | `Beispieldorf` |
  | quelle | record type from the fixed list | `Taufe`, `Heirat`, `Sterbeeintrag`, `Urkunde`, `Brief`, `Foto`, `Militär`, `Zeitung`, `Interview` |
  | lesung | only where it applies | `maschinell-ungeprüft` |

  The list of allowed terms lives in `05_register/`; a new term is a
  decision. Where a knowledge base indexes tags, they are the way into it:
  a title search finds little in per-folder summaries. Tags written by an
  ingest model are free text — map them to this list before relying on
  them (`dokumenten-wissensbasis.md` §7).
- **Findbuch der Familienunterlagen.** One row per unit — album, box,
  bundle, Familienstammbuch, bible, letters — *including what relatives
  hold*: title · date range (Laufzeit) · extent · keeper and how it came to
  them · condition · digitised (yes / partly / no, and where) · whom to ask
  for access. It is the survey of home sources: it tells the next interview
  what to ask for, and keeps "Tante Erna has the album" from being lost.
  Template: `assets/vorlagen.md` §16.

## 7. Fotos und Bilddateien / Photos and image files

- **Master files are never altered — metadata included.** Writing IPTC or
  XMP into a file changes its checksum: citations by hash break, and an
  ingest pipeline takes the file for a new document. Embed metadata in the
  working copy; for the master use a sidecar (`.xmp`, or the note in
  `assets/vorlagen.md` §17).
- Worth recording (IPTC/XMP field names): Description — who, what, where,
  left to right · Date Created — the date of the photograph or its estimate
  with the reason for it, *not* the scan date a scanner writes by default ·
  Creator — photographer or studio · Source — who holds the original, album
  and page · Person Shown — register IDs · Keywords — the controlled tags ·
  Copyright Notice and Rights Usage Terms.
- **Who is pictured is a statement by someone.** Record who identified the
  person, when, and how sure they were (`interview-oral-history.md`), and
  give it a status like any other claim. Resemblance, a caption in another
  tree and automatic face grouping are hints, not identification.
- Keep the file name meaningful all the same: platforms strip metadata.
- **Terms at capture time.** With every file from an archive or portal,
  note the terms it came under — private research only, publication with
  permission, free. Whether an image may appear in a published tree is
  decided by that note, not from memory (`quellen-deutschland.md` §8).

## 8. Aufbewahren und Aussondern / Keeping and weeding

Appraisal, applied to a research project.

- **Never weeded:** masters; dated GEDCOM exports taken before match
  decisions (the record to roll back to — never overwritten);
  correspondence (the provenance of every copy received, with fees and
  terms); rejected matches, overrides and disproven hypotheses with their
  reasons.
- **May be weeded, by the user's decision only:** exact duplicates (same
  checksum), superseded working copies, failed scans. Move to
  `_aussortiert/` first, delete later, and leave one line in the log: what,
  when, why.
- **Taking something out of the tree** is weeding too and follows the same
  rule — evaluate, document, keep it reversible: `smart-match-pruefung.md`
  §6.
