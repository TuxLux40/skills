# Zitieren und Dokumentieren / Citation and documentation

Goal: a stranger can walk from any fact in the tree to the exact entry in the
exact volume, and can see how certain the conclusion is and why.

## 1. Citation anatomy

German archival convention (repository → Bestand → Signatur → place in volume)
combined with the *Evidence Explained* layering (the original + the form you
used). Elements, in order:

1. **Verwahrende Stelle / Repository** (archive, parish, Standesamt)
2. **Bestand / fonds or collection**, **Signatur / call number**
3. **Titel der Einheit** — parish or office, record type, years covered
4. **Fundstelle** — page (S.) or folio (Bl. … r/v), entry number (Nr.), year
5. **Eintrag** — type of event, principal person(s), date of event
6. **Zugriffsweg / form used** — "Digitalisat", portal, permalink or image
   number, date viewed; or "Original eingesehen am …"; or "Kopie vom Archiv
   erhalten am …"
7. **Art der Quelle** — Original, Zweitschrift, Abschrift, Index

Examples (fictional data, real pattern — do not reuse as facts):

```
Kirchenbuch:
Bistumsarchiv Musterstadt, Pfarrei St. Peter Beispieldorf, KB 4
(Taufen 1770–1809), S. 112, Nr. 23: Taufe Johann Heinrich Muster,
14.03.1788. Digitalisat: Matricula, <Permalink>, Bild 58
(eingesehen 2026-11-14). Original.

Personenstandsregister:
Stadtarchiv Musterstadt, Standesamt Musterstadt-Mitte, Heiratsregister
1891, Nr. 204: Heirat Muster/Beispiel, 16.05.1891, mit Randvermerk vom
03.02.1920. Kopie des Registereintrags, vom Archiv erhalten 2026-10-02.
Erstregister.

Index only (finding aid, to be replaced once the image is seen):
"Deutschland, ausgewählte Geburten und Taufen", Indexeintrag Johann H.
Muster, ~14.03.1788, Beispieldorf; MyHeritage (eingesehen 2026-11-14).
Index eines Films; Original NICHT eingesehen.

Online tree (lead, never as proof of a fact):
Stammbaum "Familie Beispiel", verwaltet von <Nutzername>, MyHeritage,
Profil Johann Heinrich Muster (eingesehen 2026-11-14). Ungeprüfte
Kompilation; angegebene Quelle: keine.

Oral / family source:
Mündliche Auskunft von <Name>, Enkelin der Betroffenen, Gespräch am
2026-08-03 in <Ort>, Notizen im Besitz d. Verf. Sekundärinformation.
```

Rules:

- Cite **what you actually used**. Saw only the index → cite the index and say
  so. Never cite the Kirchenbuch on the strength of someone else's tree.
- One citation per fact; reuse a source record, but give each fact its own
  Fundstelle.
- Keep the portal's image number *and* the archival Signatur — portals come
  and go, Signaturen persist.
- Bilingual output: keep repository names and titles in the original language;
  translate only the connective text.

## 2. Fact-level sourcing in tree software

- Attach citations to the **event/fact**, not to the person.
- Store alternative/conflicting values as additional facts with their own
  citation and a note which is preferred and why — do not delete.
- Use the certainty field if available (GEDCOM QUAY 0–3) consistently: 3 =
  original/primary and direct, 2 = secondary, 1 = questionable/estimated,
  0 = unreliable; and put the skill's status word in the note.
- Estimated dates are entered as estimates (`ABT`, `EST`, `CAL`, `BEF`, `AFT`,
  `BET … AND …`), with a note saying from what they were derived.
- Keep a marker (tag/custom fact) for **unverified hypotheses** so they can be
  filtered out of exports and never synchronise to public trees.
- **Status prefix:** where the tree is kept on a site without a status field
  (MyHeritage), begin the fact's citation or note with `[belegt]`,
  `[wahrscheinlich]` or `[möglich]`; for overridden matches add
  `Nachprüfen: <record that would settle it>`.
- **Online tree as master:** the default setup is the MyHeritage tree as the
  authoritative copy plus a **dated GEDCOM export** before every round of
  match decisions (`90_export/JJJJ-MM-TT_<baum>.ged`). The export is the
  backup and the input for `scripts/gedcom_plausi.py`. GEDCOM transfer loses
  data (custom tags, media links, some citation detail) — do not treat a
  re-import as lossless.

## 3. Files and folders

Name files so they sort and identify themselves without the folder:

```
<JJJJ-MM-TT>_<Ereignis>_<NACHNAME>-<Vorname>_<Ort>_<Archivkürzel>-<Signatur>_<S|Bl|Nr>.<ext>
1788-03-14_Taufe_MUSTER-Johann-Heinrich_Beispieldorf_BAM-KB4_S112-Nr23.jpg
1891-05-16_Heirat_MUSTER-BEISPIEL_Musterstadt_StAM-HR1891_Nr204.pdf
```

- ISO dates; unknown parts as `0000`/`00`; no umlaut loss needed on modern
  filesystems, but be consistent.
- Keep the **unaltered download/scan** (master); put crops and enhanced
  versions beside it with a suffix. Record checksums if the collection is
  meant to last. Prefer TIFF/PNG or original JPEG for masters, PDF/A for
  documents.
- Suggested structure:

```
genealogie/
  00_forschungsprotokoll/     research log, one file per session or question
  10_quellen/                 by repository → Bestand → unit (provenance!)
  20_personen/                one note per person, ID in the filename
  30_familien-orte/           place and family-group notes
  40_hypothesen/              unproven links, rejected matches, overrides
  50_korrespondenz/           archive requests and replies
  90_export/                  dated GEDCOM backups
```

Sources are filed by **provenance** (where they come from), not by the person
they mention — one register page names many people; link from person notes.

## 4. Person identifiers

Give every person a stable ID independent of any website. Kekulé/Ahnentafel
numbers (proband 1, father 2n, mother 2n+1) work for direct ancestors; use a
neutral running ID (`P0001`) for everyone and store Kekulé as an attribute,
because Kekulé numbers shift when the proband changes and do not cover
siblings. Record the MyHeritage/FamilySearch IDs as external references.

## 5. Research log (Forschungsprotokoll)

One entry per search, written at the time:

| Field | Content |
|-------|---------|
| Datum | when searched |
| Forschungsfrage | which question this serves |
| Quelle | full citation of what was searched (volume, years) |
| Suchumfang | names and variants, years, pages actually read |
| Ergebnis | found (→ citation) / **nicht gefunden** / nicht lesbar / Lücke |
| Bewertung | source–information–evidence |
| Folgeschritt | next action |

Negative results with their scope are the most valuable entries: they stop
repeated searches and can become negative evidence.

Session summary for the knowledge base (when the user asks to document):
question(s) worked on → sources consulted → findings with status → conflicts
open → hypotheses rejected and why → next steps → files added.

## 6. Publishing

- Mark hypotheses as such in text and charts (dashed lines, "vermutlich").
- State the cut-off date of the research and how AI tools were used.
- Deposit a copy (GEDCOM + sources + log) where it survives you: family,
  regional society, CompGen projects.
