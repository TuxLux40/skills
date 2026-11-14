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

Published work (compilation — a lead that names a source to follow):
MUSTER, Erika, 1998. Ortsfamilienbuch Beispieldorf 1650–1900. Musterstadt:
Verein für Familienkunde Musterstadt, S. 214, Familie Nr. 1023.
Kompilation; dort angegebene Quelle: KB Beispieldorf, Taufen 1788.
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
- **Published works** — Ortsfamilienbuch, local history, article, web page
  — follow ISO 690: author, year, title, edition, place, publisher, then
  page and family or entry number; online sources add `[online]`,
  `[Zugriff am: …]` and `Verfügbar unter: …`. The standard fixes elements
  and their order, not punctuation: be consistent. (The German edition DIN
  ISO 690:2013-10 is withdrawn; ISO 690:2021 is current.) Always add what
  the work names as its own source — that is where the evidence is.
- A family document found through a document knowledge base is cited in the
  form given in `dokumenten-wissensbasis.md` §4.

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
  match decisions (`90_export/JJJJ-MM-TT--<Baum>.ged`). The export is the
  backup and the input for `scripts/gedcom_plausi.py`. GEDCOM transfer loses
  data (custom tags, media links, some citation detail) — do not treat a
  re-import as lossless.

## 3. Files, names, registers

Where files go, how they are named, the person and place registers, tags,
photos and what is kept: `ablage-und-erschliessung.md`. Two rules from
there bear on every citation:

- **Master files are never altered** — the scan, download or recording as
  received, its metadata included. Edited versions sit beside the master
  with a suffix.
- **Provenance stays visible**: repository and Signatur in the file name,
  and a sidecar note holding citation, access date, original URL, checksum
  and the terms of use the file came under.

## 4. Research log (Forschungsprotokoll)

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

The log also holds the **Parkplatz**: side finds that do not serve the
current question, one line each with source. They are picked up as their
own question later, not followed on the spot.

Session summary for the knowledge base (when the user asks to document):
state line → question(s) worked on → sources consulted → findings with
status → conflicts open → hypotheses rejected and why → parked finds →
requests waiting → the one next step → files added. The next session opens
from it (`ausgabeform.md` §3).

## 5. Publishing

- Mark hypotheses as such in text and charts (dashed lines, "vermutlich").
- State the cut-off date of the research and how AI tools were used.
- Images of records and photos: publish only what the terms noted at
  capture allow (`ablage-und-erschliessung.md` §7).
- Deposit a copy (GEDCOM + sources + log) where it survives you: family,
  regional society, CompGen projects.
