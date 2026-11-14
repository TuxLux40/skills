# Dokumenten-Wissensbasis / Document knowledge base (smart-okf, OKF, MCP)

When the user's family papers — certificates, Familienstammbuch, letters,
photos, military and refugee papers — have been turned into Markdown by an
ingest pipeline and are reachable through the file system or an MCP
connector (for example a Grav site). In this repository the pipeline is the
sibling skill `smart-okf`; the rules hold for any pipeline of that kind.

The pipeline answers "what is in my documents?". This file answers a
narrower question: **what may a line from those Markdown files carry in a
genealogical conclusion?**

## 1. Schichten / Layers

| Layer | What it is | Good for | Evidence role |
|-------|-----------|----------|---------------|
| **Original** | the paper, the photo, the register page | — | the source; classify it per `methodik-gps-quellenkritik.md` |
| **Datei** | scan or photo in the storage; listed under `sources:`, SHA-256 under `source_hashes` | reading and citing | image copy of the original |
| **Transkript** | machine text of the file (`.okf-transcripts/`): text layer, OCR, or a vision model | exact wording, searching | derivative; for handwriting a *machine reading* |
| **Aggregat** (`type: FolderSummary`) | one Markdown per folder: orientation summary, then one `## section` per source file | learning what exists and where | finding aid: a model's extraction from the transcript |
| **Matter / Synthesis** (`type: Matter`, `type: Synthesis`) | cross-folder write-ups: Matters, Conflicts, Patterns, Open actions | a map of where to look | machine inference — a hint, like a Smart Match |

Cite the original document, and say which layer you actually looked at.

## 2. Wo die Garantie der Pipeline endet / Where the pipeline's guarantee ends

smart-okf checks every extraction against the text it was made from and
marks a failure in the file as `_Verification: FLAGGED — <reason>_`. For its
own purpose a file without that line may be used without reopening the
original. That guarantee covers **aggregate = transcript**. It does not
cover

1. **transcript = image** — whether OCR or the vision model read the page
   correctly, and
2. **document = person** — whom the document concerns.

Genealogy fails at exactly these two points. So in this skill:

| The source file is … | Section without FLAGGED | Section with FLAGGED |
|----------------------|-------------------------|----------------------|
| born-digital text, or cleanly typed or printed in roman type (modern certificates, typed letters, e-mail, spreadsheets) | usable as a reading of the document; then evaluate the document itself as usual | not usable until checked against the file |
| handwriting of any kind (Kurrent, Sütterlin, modern), Fraktur print, forms filled in by hand, stamps, damaged or low-resolution scans, photos of register pages | **maschinell gelesen, ungeprüft**: names, dates, places, numbers and relationships are leads until the user has confirmed them at the image — until then at most `[möglich]` and not in the tree | the same, and distrust the whole section |

- **Why so strict for handwriting.** Classic OCR fails on old hands visibly:
  the transcript is garbage. A vision model fails invisibly: it returns a
  fluent, plausible name or date. It happens exactly where identity is
  decided — digits (1/7, 3/5/8, 0/6), surnames, abbreviations, Latin forms.
  `[unclear]` in a transcript marks a doubt the model noticed; its absence
  proves nothing.
- **Which row applies.** File type in `sources:` (image or scanned PDF
  versus text file), the date of the document, the script named in the
  transcript or description. In doubt: handwriting.
- **Wording** is quoted from the transcript or the image, never from the
  aggregate; orientation summaries, timelines and Patterns are generated
  prose and never quoted as source text.
- **Identity.** A document lying in a person's folder, or tied to a person
  by a Matter or the Synthesis, is not thereby about that person. The
  folder shows how something was filed — provenance, or a former keeper's
  guess — not pertinence. Same-name links go through the identity check
  (`smart-match-pruefung.md`) like any other hint.

## 3. Finden und Abdeckung / Retrieval and coverage

- **File-system access:** follow smart-okf's own retrieval ladder
  (synthesis → matter files → navigation → aggregates → transcripts → git
  history); it is described in that skill's `SKILL.md`.
- **MCP access:** find out what the connector's search covers. A page list
  that matches titles and routes only is not a full-text search. Then
  navigate instead (synthesis → folder index → aggregate) and log a miss as
  "nicht geprüft (nur Titelsuche)", never as "nicht gefunden".
- **Coverage before any negative statement.** Is the folder ingested at all
  (an aggregate exists, its `sources:` match the files present)? When was
  the last ingest? Does the pipeline read the file type? smart-okf reads
  PDF, TXT, DOCX, EML, CSV, XLSX, PNG and JPEG (current list in its
  `app/constants.py`); TIFF masters, audio recordings, GEDCOM files and
  Markdown notes are skipped without a message.
- Aggregates are per folder and not recursive. A folder that looks partly
  covered is a warning sign — check its subfolders.
- "Not in the knowledge base" ≠ "not in the archive" ≠ "does not exist".
  Log which of the three you established.

## 4. Zitieren / Citing a document found this way

```
<Dokument wie üblich: Aussteller/Verfasser, Art, Datum, Personen>;
Familienarchiv <Name>, <relativer Pfad aus sources:>, SHA-256 <erste 12 Stellen>;
eingesehen als <Bild | Transkript | Aggregat> am <JJJJ-MM-TT>
[; Lesung maschinell, ungeprüft].
```

Paths change when folders are renamed; the hash still identifies the file
(the full value is in the aggregate's frontmatter). For a privately held
original, name who holds it. The status prefix goes in front as usual.

## 5. Synthese als Zubringer / What the synthesis is good for

- `Conflicts` → each becomes a conflict analysis (`assets/vorlagen.md` §4),
  after both documents have been looked at.
- `Patterns` and `Matters` → candidates for the connection scan
  (`faecher-modus.md` §6): write each as a prediction, then test it.
- `Open actions` → candidates for the research plan, not jobs to carry out
  unasked.

The synthesis was built to join modern paperwork by reference numbers. Old
documents share names, not numbers, so its links between them rest on names:
treat every such link as a possible namesake until checked.

## 6. Schreiben / Writing rules

- **Never edit generated files** — aggregates, matter files, synthesis,
  transcripts. They are overwritten at the next ingest, and their hashes are
  the provenance chain. A misreading goes into the research log or source
  sheet and is reported to the user, so it can be corrected at the file and
  re-ingested.
- **Research notes are not sources.** Logs, source sheets, proof arguments
  and session summaries stay where the ingest does not pick them up as
  documents: a separate notes tree, or Markdown files (smart-okf ignores
  `.md` input for exactly this reason). Never save text you wrote as `.txt`,
  `.pdf` or `.docx` inside an ingested folder — the next ingest would hand
  your own conclusion back as a document fact. That is circular evidence.
- **Sources made during the project are documents**: interview recordings
  and their transcripts, gravestone photos, archive replies. File them with
  who, when and how, so they can be ingested like the rest.
- Keeping masters in a format the pipeline skips (TIFF): put a readable
  derivative (PNG, JPEG or PDF) beside the master. Naming and filing follow
  the user's structure; the sibling skill `dokumenten-organisation` covers
  the method.
- Write to a knowledge base only when the user asks to document, and where
  they said.

## 7. Zugang über MCP / Connector notes

- Check once what the connector account may do: read or write, pages only
  or media too.
- A connector that serves pages usually exposes the aggregates only —
  neither the hidden transcript folder nor the scans. Then the aggregate is
  the lowest layer you can look at: say so in the citation, and do not
  quote wording.
- If scans are reachable, open the image for everything that will carry a
  conclusion. If only Markdown is reachable, ask the user for the one
  passage that matters, as a concrete question: "Heiratsurkunde 1891, Zeile
  'Vater des Bräutigams': steht dort 'Wilhelm' oder 'Wilh.'?"
- Connector unreachable or page missing → "nicht geprüft"; go on with what
  is available.
