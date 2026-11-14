# Fächer-Modus / Divergent mode (auffächern, dann bündeln)

For dead ends (toter Punkt) and open planning questions: generate research
directions widely, under deliberately different vantage points, then narrow
hard. Method adapted from the `adhd` skill (see Credits): isolated parallel
branches, no evaluation while generating, a separate critic pass afterwards.
Frames, scoring and output are built for genealogical research.

> **Firewall.** Everything this mode produces is a **lead** (Suchansatz),
> not a finding. Nothing from it gets a status above `[möglich]`, enters the
> tree, or is cited. A connection the model "sees" between two data points
> weighs as much as a Smart Match: nothing, until it has passed the identity
> check in `smart-match-pruefung.md`.

How it fits with `ausgabeform.md`: this mode widens what you *consider*;
the output rules narrow what you *show*. Generate wide, show narrow.

## 1. Vorprüfung / Gate

A run costs about ten sub-agent calls — five to ten times a direct answer.

**A. Asked for** — "Fächer-Modus", "ADHD-Modus", "neue Ansätze", "quer
denken", "brainstorm", "was kann ich noch tun?" at a stated dead end → run.

**B. Not asked for** — run unasked only if all three hold, and say in one
line that you are doing so:

1. **Standardweg erschöpft.** The record types that should exist for this
   place, confession and period (`quellen-deutschland.md`) are searched and
   logged, or verifiably lost or closed; items 1–8 of the brick-wall
   checklist (`erweiterte-recherche.md` §5) are done. Reasonably exhaustive
   research starts with the obvious sources — if one is open, do it first.
2. **Offene Frage.** There is no single canonical next source.
3. **Im Umfang.** The question concerns the direct line or a family group
   in scope.

A search spiral (three empty searches on one question) triggers this check,
not the run itself. If B fails, answer directly and name what is still open
on the standard path.

## 2. Lagebild / The brief

Write it once; every branch gets the identical text.

```
FRAGE:     eine Forschungsfrage zu einer identifizierten Person
PERSON:    Name · * Datum Ort · ∞ Datum Ort, Partner · † Datum Ort
           — nur [belegt]/[wahrscheinlich], je mit Kurzquelle
UNBELEGT:  was Baum, Überlieferung oder fremde Bäume behaupten
GEPRÜFT:   bisherige Suchen mit Umfang und Ergebnis
           (auch "nicht gefunden", auch "nicht geprüft")
RAUM/ZEIT: Pfarrei, Standesamt, Territorium zum Zeitpunkt, Konfession,
           Beruf, Stand
```

No conclusion, no favourite hypothesis, no "vermutlich" in the brief —
branches anchor on whatever it suggests. Persons with year and place.

## 3. Phase 1 — Auffächern / Diverge (no critic)

1. Pick five frames from §7 (three for a small question): from at least
   two groups, and always one `wild`.
2. Spawn one sub-agent per frame, **in parallel and isolated**. Each gets
   the brief, its one frame and the instruction below — nothing else. No
   branch sees another branch's output, the log's hypotheses or your ideas.
   Branches that see each other converge on the first idea, and the run
   collapses into one wider thought.
3. Branches do not research: no tools, no searching, no statements about
   what a record or archive contains.

Instruction for each branch (translate if the user does not write English):

```
You generate research leads. You do not evaluate them.
Look at the brief only from the vantage point below.
Write 6 distinct leads, one sentence each, plus one clause on why this
vantage point suggests it. Do not rank, hedge or judge feasibility.
Not accepted as leads: "check the parish register / civil register",
"look at other online trees", "search the big genealogy sites" — the
standard path is done. Go past the obvious.
Use no tools. Do not state as fact what a record or archive contains;
write "if it exists".
Answer in <language>. Output a numbered list only.

VANTAGE POINT: <frame text from §7>
BRIEF: <brief from §2>
```

**Ersatzlauf / without a sub-agent tool.** Work through the frames one at a
time, writing each frame's leads without going back to earlier ones, and
label the result "Ersatzlauf ohne Isolation". That is a structured
checklist, not this method: the leads will lean towards your first idea.
Say so rather than present it as a full run.

## 4. Phase 2 — Bündeln / Focus (critic on)

Yours, with the complete research log at hand.

1. **Gegen das Protokoll abgleichen / dedupe.** A lead already searched
   with the same scope is dropped. If the earlier search was narrower, keep
   the lead and word it as the wider search.
2. **Bewerten / score** every lead from 0 to 3:

   | | 0 | 1 | 2 | 3 |
   |---|---|---|---|---|
   | **T** Trennschärfe / diagnostic power | any outcome would be read as support | narrows the field a little | clearly favours or weakens one hypothesis | decides: direct evidence from an independent, contemporaneous source — or a hard exclusion |
   | **M** Machbarkeit / feasibility | series never existed, is lost, or is closed to the user | existence or access unverified; or on-site, costly, slow only | exists; reachable by request or login portal | open online now |
   | **N** Neuheit / novelty | standard path, or already planned | known technique not yet applied here | record group or person cluster new to this project | changes the question itself |

   **Rang = T × M**; N only breaks ties. A decisive record nobody can get is
   worth nothing today; an easy search that cannot change the conclusion is
   worth nothing ever. Whatever you could not verify about existence or
   access is marked `*(verify)*` and scores M ≤ 1 until checked.
3. **Fallen markieren / flag traps** — attractive but unsound. Exclude them
   from the shortlist and list each with a one-line reason:
   - same name treated as same person;
   - rests on other online trees or an unsourced compilation (circular);
   - not diagnostic: the outcome would count as support either way;
   - silence read as evidence although the record series has gaps;
   - impossible in time or distance against the proven facts;
   - a record series that did not exist yet at that place and date;
   - closed by protection periods for someone who is not entitled;
   - prestige pull: nobility, coat of arms, famous namesake, surname
     etymology as proof of kinship;
   - DNA over-read: small segments, endogamy, a single match
     (`dna-myheritage.md`);
   - paying for an index while the original is open elsewhere.
4. **Gruppieren / cluster** the rest into three to six groups by underlying
   angle, not by keyword: "Umfeld statt Person", "Behördenpapier", "Besitz
   und Erbe", "Ort und Zuständigkeit", "Identität gegenprüfen", "Nachfahren
   und DNA".
5. **Vertiefen / deepen the top three** by rank, traps excluded. The
   best-ranked lead with N ≥ 2 and T × M ≥ 4 is always among them and marked
   ★ — the non-obvious pick; if none qualifies, say so instead of promoting
   one. One sub-agent per lead, or yourself. Deepening may look things up
   (finding aids, holdings overviews, this skill's references) under the
   normal rules: blocked means "nicht geprüft". Each lead becomes a
   **Suchauftrag**:

   ```
   Hypothese:        ein Satz
   Vorhersage:       stimmt sie → Quelle Q zeigt X; stimmt sie nicht → Y.
                     Ein Negativbefund zählt nur, wenn die Reihe für
                     <Jahre> lückenlos ist — Lücken zuerst prüfen.
   Quelle & Zugang:  Bestand, verwahrende Stelle, Portal oder Anfrage,
                     Jahre, Namensvarianten
   Tragende Annahme: was gelten muss, damit der Ansatz trägt
   Erster Schritt:   eine Handlung, höchstens zehn Minuten
   Aufwand:          Zeit / Kosten, soweit bekannt
   Folgeansätze:     2–4, je nachdem ob der Ansatz trifft oder scheitert
   ```

   A lead that cannot be written as a prediction is a trap by definition.
6. **Übergabe / hand-over.** A Suchauftrag enters the normal workflow at
   step 3 (plan) and step 4 (search and log). What the search finds is
   evaluated like any other source; the lead itself is never evidence.

Leads with T = 3 but M ≤ 1 go to the log as **Fernziele** — re-check them
when access changes (new digitisation, an on-site visit, a relative found).

## 5. Ausgabe / Output

```
Frage: <eine Zeile, mit Umdeutung falls vorgenommen>
Lauf:  <n Rahmen × m Ansätze · isoliert | Ersatzlauf ohne Isolation>
Shortlist:
1. ★ <Ansatz> [T3 M2 N3] — Vorhersage: … — Erster Schritt: …
2. <Ansatz> [T2 M3 N1] — …
3. …
Fallen: <Ansatz> — <Grund>            (höchstens 5, "+n im Protokoll")
Querfrage: <eine Frage, die das Problem neu öffnet, falls nichts trägt>
Nächster Schritt: <einer>
```

The complete fan — every lead by group with its chips, every trap, the
Fernziele — goes into the log (`assets/vorlagen.md` §13) and into the reply
only on request ("zeig alle"). Take a position: "here are thirty ideas,
you choose" is a failed run.

## 6. Querverbindungen / Connecting data points you already hold

Often enough without a full run, and needs no sub-agents.

1. Fill the **Personen-Netz** (`assets/vorlagen.md` §14) from every captured
   record: each named person per record, with role, place or address, date,
   stated age, occupation, and whether they signed or made a mark.
2. Scan for:
   - a person recurring at *different* family events;
   - a witness or godparent whose surname is a maiden name somewhere in the
     family group;
   - the same house, farm, street or employer;
   - the same place of origin in entries that look unrelated;
   - an informant who also reports for another household;
   - a child named after a godparent — and that godparent's surname;
   - two events for "one" person that collide in time or distance (→ two
     people);
   - a signature that changes, or someone who signs once and later makes a
     mark;
   - stated ages that drift from record to record;
   - someone missing where they should appear (not among the heirs; never a
     godparent in a family that always chose siblings);
   - DNA-cluster surnames or places that reappear in the table.
3. Every hit is a hint. Write it as a prediction (§4.5), then check it.

## 7. Rahmen / Frames (genealogy pack)

A frame is a vantage point that re-poses the whole question — not an expert
persona. Give the text to the branch verbatim.

| Frame | Vantage point | Group |
|-------|---------------|-------|
| **Umfeld** (FAN) | Ignore the target person. Work only with the people around them: godparents, witnesses, informants, neighbours, landlords, employers, fellow travellers. Who recurs, who is unexplained, whose own records would mention the target in passing? | umfeld |
| **Frauenlinie** | Follow only the women: wife, mother, sisters, widows and their later marriages, godmothers. Maiden names connect families that the surname hides. | umfeld |
| **Nachfahren abwärts** | Do not go up. Go down from the siblings and cousins of the last proven generation to people alive today. Who inherited the papers, photos, letters, the family bible — and whose DNA test would help? | umfeld |
| **DNA-Blick** | Reason only from shared DNA: which cluster has no paper explanation, which expected cousin is missing, whose test would split the competing hypotheses? | umfeld |
| **Amtsstube** | You are every office that had to open a file on this person: tax, conscription, residence registration, poor relief, guardianship, citizenship, emigration consent, insurance, pension, court. What had to be written down, and why? | papier |
| **Geld und Besitz** | Follow property, not people: inheritance, land and mortgage registers, leases, debts, dowries, guild and burgher fees, compensation claims. Who paid, who inherited, who stood surety? | papier |
| **Beruf und Stand** | The occupation is the key. What does this trade, employer, estate or service write down by itself — miners' fund, railway, guild, garrison, school, church office, servants' books? | papier |
| **Zweite Überlieferung** | Assume the obvious record is lost or wrong. Which independent second series recorded the same event: duplicate register, civil beside church, newspaper notice, death card, gravestone, probate, marginal note, the other party's files? | papier |
| **Ort statt Person** | Research the place as if the person did not exist: parish and office boundaries at that date, changes of jurisdiction, neighbouring parishes, the nearest mine, garrison, port or factory, where people from this village went to work or to marry. | raum |
| **Zeitleiste** | Lay out every proven date. Look at the gaps and the collisions. What happened to this place in the gap years — war, epidemic, closure, boom, border change? Where must the person have been? | raum |
| **Wanderung** | Treat the person as freight: departure, transit, arrival, registration at each end. Who from the same village went first, and where to? | raum |
| **Gegenprobe** | Assume the current identification is wrong and two people bore this name. Where would the *other* one appear? What would guarantee that the right one is never found — wrong parish, confession, spelling, decade? Turn each answer into a check. | probe |
| **Namensblick** | Treat names as data produced by naming rules: patronymics, farm names, Latin and dialect forms, translation across a border, children named after godparents and grandparents. What do the children's names predict about the unknown generation? | probe |
| **Tragende Annahme streichen** | List what everyone treats as fixed: the spelling of the surname, the birthplace taken from a late record, the age at death, legitimacy, the confession, "born where baptised", the father named in the tree. Delete one at a time. What becomes possible? | wild |
| **Kinderfrage** | You have never heard of archives. Whom would you simply ask? What is written on the back of the photo, in the box in the attic, on the grave, in the family's stories and nicknames? | wild |
| **Null Euro, eine Stunde** | No money, one hour, only what is open online right now. What is the crudest check that would kill or support the hypothesis today? | wild |
| **Unbegrenzt** | Unlimited time and money: read every page, visit on site, hire help, test every living cousin. What would the maximal version do that nobody has tried — and which small piece of it is affordable now? | wild |
| **Alle Namensträger** | No target person at all. Collect everyone bearing the surname and its variants in this place and period, and sort them into households. The target is what remains. | wild |

Where to start, by kind of dead end (always add one `wild`; vary it between
runs — a second run with other frames is legitimate):

| Sackgasse | Frames |
|-----------|--------|
| Eltern unbekannt / parents unknown | Umfeld, Namensblick, Geld und Besitz, Frauenlinie |
| Person verschwindet oder taucht auf / vanishes or appears from nowhere | Wanderung, Amtsstube, Beruf und Stand, Ort statt Person |
| Zwei Kandidaten gleichen Namens / namesakes | Gegenprobe, Zeitleiste, Umfeld, Alle Namensträger |
| Quelle verloren / record lost or gap | Zweite Überlieferung, Amtsstube, Geld und Besitz, Nachfahren abwärts |
| Ereignis im Ausland / event abroad | Wanderung, Amtsstube, Zweite Überlieferung, Nachfahren abwärts |
| DNA-Treffer ohne Papierweg / DNA without a paper trail | DNA-Blick, Nachfahren abwärts, Umfeld, Gegenprobe |

A new frame earns its place if it brings its own vocabulary and its own
posture (naive, adversarial, maximal …) and reliably yields leads the others
do not.

## 8. Fehlerbilder / How this mode fails

- **Verkleidete Einengung.** Ten variants of one assumption are not a fan.
- **Unsortierter Haufen.** No shortlist, no position taken.
- **Verunreinigung.** A favourite hypothesis in the brief; or branches
  written one after another in one context but reported as isolated.
- **Ansatz wird Befund.** A plausible story lands in the log as a result.
- **Fächer statt Standardweg.** The gate was skipped.
- **Auffüllen.** Stop when new leads repeat the shape of old ones; do not
  pad to reach a number.

## 9. Kalibrierung und Kosten / Calibration and cost

- Default 5 frames × 6 leads; small question 3 × 4; about ten sub-agent
  calls including deepening.
- The benefit for genealogy is unmeasured. Upstream reports gains over a
  single direct answer on six engineering problems, judged by a model of the
  same family, and lists that, the small set and a study without measurable
  benefit for human designers among its own limitations. Use the fan as a
  cheap way not to overlook a record group. What keeps it honest is the
  gate, the prediction requirement and the normal evidence workflow.

## Credits

Method adapted from **ADHD — a skill for agents** by Udit Akhouri and
contributors (<https://github.com/UditAkhourii/adhd>, MIT License, © 2026
ADHD contributors): isolated parallel divergence under frames, separate
critic pass, trap flags, deepening of the survivors. The gate, the brief,
the T × M scoring, the trap list, the Suchauftrag, the frame pack and the
connection scan are specific to this skill.
