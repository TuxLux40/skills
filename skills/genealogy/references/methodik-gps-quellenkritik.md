# Methodik: Genealogical Proof Standard + Quellenkritik

Two traditions, one workflow. The Anglo-American **Genealogical Proof Standard
(GPS)** defines when a conclusion counts as proven; German historical
**Quellenkritik** defines how to interrogate a single source. Use both.

## 1. GPS — five elements

1. **Reasonably exhaustive research** (umfassende Recherche): all sources a
   competent researcher would expect to bear on the question, not all sources
   in existence. Document what was searched and what was unavailable.
2. **Complete, accurate citations** (vollständige Quellenangaben).
3. **Analysis and correlation** (Auswertung und Abgleich) of all evidence.
4. **Resolution of conflicting evidence** (Auflösung von Widersprüchen).
5. **Soundly reasoned, written conclusion** (schriftlich begründeter Schluss).

A conclusion that skips one element is at most *wahrscheinlich*. "Proven" is
always provisional: new evidence reopens the question.

## 2. Evidence analysis — three independent axes

Classify separately; do not collapse into "good/bad source".

| Axis | Categories | Question |
|------|-----------|----------|
| **Quelle / Source** | Original · Abschrift/Derivat (duplicate, transcript, abstract, index, translation) · Kompilation/authored work (OFB, tree, family history) | How far is this object from the first recording? |
| **Information** | Primär (informant witnessed the event) · Sekundär (hearsay) · Unbestimmt (informant unknown) | Who supplied *this particular statement* and how did they know? |
| **Beleg / Evidence** | Direkt (answers the question by itself) · Indirekt (needs combining) · Negativ (meaningful absence) | How does it bear on *this research question*? |

One record holds mixed information. A 1885 Sterbeurkunde: death date and place
are usually primary (informant present or household member); the deceased's
birth date, birthplace and parents' names are secondary, sometimes guesswork by
a neighbour or landlord. Always check **who the Anzeigende(r) was**. If the
informant is not named, the information is *unbestimmt* — do not guess one.

Typical classifications:

| Record | Source | Notes |
|--------|--------|-------|
| Kirchenbuch (Erstschrift) | Original | Often entered days later from notes; check for chronological order breaks |
| Kirchenbuch-Zweitschrift / Duplikat | Derivative (near-contemporary) | Copied annually for the authorities; copying errors and omissions; sometimes the only survivor |
| Personenstandsregister Haupt-/Nebenregister | Original / official duplicate | Randvermerke (marginal notes) on later marriage, death, name changes — read them |
| Beglaubigte Abschrift, Urkunde aus dem Register | Derivative | Only reproduces selected fields |
| Ortsfamilienbuch / Ortssippenbuch | Compilation | Family reconstitution by an author; excellent finding aid; verify each link |
| Ahnenpass | Compilation of certified extracts | See pitfalls |
| Online index (Ancestry, MyHeritage, FamilySearch) | Derivative | Finding aid; cite the image, not the index, once seen |
| Online tree | Compilation | Lead only |
| Maschinentranskript (OCR, HTR, Vision-Modell) | Derivative (machine reading) | Printed roman type: usually reliable. Handwriting and Fraktur: provisional until checked at the image; a vision model's errors look plausible |
| KI-Zusammenfassung eines Dokumentenarchivs (e.g. smart-okf aggregate, synthesis) | Finding aid — derivative of a derivative | Cite the document, not the summary; see `dokumenten-wissensbasis.md` |
| Grabstein, Totenzettel, Todesanzeige | Original object, secondary information for birth | Good for death, weak for birth data |
| Adressbuch | Original compilation | Residence/occupation with a time lag of ~1 year |

## 3. Quellenkritik

**Äußere Kritik (external):** Is the object what it claims to be? Provenance
(which Pfarrei/Standesamt/authority produced it, where is it held now, under
which Signatur), date of creation vs. date of event, original or copy, same
hand and ink as neighbouring entries, later additions, damage, gaps in the
volume. For digitised images: which archive's scan, which film/image number.

**Innere Kritik (internal):** Could and would the author record this correctly?
Proximity to the event; informant's knowledge; purpose of the record
(a baptism register records baptisms — the birth date is incidental);
conventions and formulae; motive to distort (age at marriage, legitimacy,
confession, "arische Abstammung", military age, inheritance); internal
consistency.

Also from German historiography: **Überrest vs. Tradition** — a record created
for administrative purposes (register, tax list, contract) is an unintentional
witness and generally more trustworthy for incidental facts than a narrative
created to inform posterity (chronicle, family history, obituary).

**Provenance principle** applies to the user's own files too: keep material
from one origin together and never "improve" a transcription to match another
source.

## 4. Correlation

- Build a timeline per person with every dated fact and its source; gaps and
  collisions become visible.
- Reconstruct the **whole family group** (all children, both marriages); a
  single line traced in isolation is where identity errors hide.
- Use the **FAN principle** (Friends/Associates/Neighbours; Paten, Zeugen,
  Nachbarn): godparents are usually kin or neighbours; recurring names link
  entries that do not name parents.
- Independent sources agreeing > many derivative sources agreeing. Two records
  with the same informant are not independent.

## 5. Negative evidence and negative results

- **Negative result:** searched, found nothing. Only worth something if the log
  shows *what* was searched (volume, years, name variants) and that the source
  is complete for that span.
- **Negative evidence:** the absence itself answers the question — no burial
  entry in a complete register across the years the person would have died
  there suggests they left; a child missing from an inheritance division
  suggests it died before.
- Never infer from silence in an index. Indexes are incomplete; check register
  gaps (Lücken) — war losses 1618–48, 1689 (Pfalz), 1945; fire; missing years.

## 6. Resolving conflicts

For each conflicting pair, write down: both values, both citations, the three
classifications for each, and the explanation. Preference order, all else
equal: original > derivative; primary > secondary information; contemporaneous
> later; disinterested > interested informant; specific > rounded. Common
innocent explanations: birth vs. baptism date, calendar change, age rounding,
Rufname vs. full name, place given at different administrative levels, clerk's
copying slip between Erst- and Zweitschrift.

If no explanation holds, the conclusion status is *ungeklärt* — say so.

## 7. Written conclusions

- **Proof statement** (Belegsatz): one sentence + citations, when direct
  evidence from sound sources agrees.
- **Proof summary** (Belegzusammenfassung): list or short narrative, when
  several pieces are needed but no serious conflict exists.
- **Proof argument** (Beweisführung): full reasoning, when evidence is
  indirect or conflicting. Structure: question → evidence → analysis →
  conflicts → conclusion.

Hedging language carries meaning — use it consistently: "ist" (belegt),
"wahrscheinlich", "möglicherweise", "nicht nachweisbar".

## 8. AI-specific discipline

- Handwriting readings by a model are **provisional transcriptions**. Mark them
  as machine-read, flag uncertain words, and have names, dates and numbers
  checked against the image by the user. Kurrent digits and month names
  (7bris = September, 8bris = Oktober, 9bris = November, Xbris = Dezember) are
  frequent error sites.
- A summary checked against its transcript inherits every misreading of that
  transcript. Verification inside a pipeline is not verification at the
  image.
- Leads a model generates — Fächer-Modus, a synthesis's "patterns", any
  connection it "sees" between records — are hypotheses. Each needs a
  prediction and a check, and none carries a status above `[möglich]`.
- Never produce a citation from memory of what a register "should" contain.
- When asked "what do you know about family X in village Y", answer from
  provided material and searchable sources only; background knowledge about a
  region is context, not evidence for individuals.
- Disclose AI assistance in anything published.

## Literatur / Further reading

- Board for Certification of Genealogists, *Genealogy Standards* (GPS).
- Elizabeth Shown Mills, *Evidence Explained* (citation and analysis model).
- Wolfgang Ribbe / Eckart Henning, *Taschenbuch für Familiengeschichtsforschung*.
- Ahasver von Brandt, *Werkzeug des Historikers* (Quellenkunde, Hilfswissenschaften).
- GenWiki (wiki.genealogy.net) — regional portals, record-type articles.
