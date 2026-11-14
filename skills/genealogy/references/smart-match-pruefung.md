# Smart-Match-Prüfung / Verifying Smart Matches and other hints

Protocol for deciding whether a profile in another tree (or an indexed record)
refers to the same person as a profile in the user's tree. Applies to
MyHeritage Smart Matches first, and equally to Record Matches, Instant
Discoveries, Theory of Family Relativity, Ancestry hints, FamilySearch Family
Tree, Geni, WikiTree, GEDBAS, and published Ortsfamilienbücher.

## 1. What each hint type actually is

| Hint | What it compares | Evidential nature | Risk |
|------|------------------|-------------------|------|
| **Smart Match** (MyHeritage) | Your tree profile ↔ another user's tree profile | Authored, derivative, usually uncited | High: copies propagate |
| **Record Match** (MyHeritage) | Your tree profile ↔ indexed record | Depends on the record; the *index* is derivative, the image may be original | Medium: right record, wrong person |
| **Instant Discovery** | Adds a whole branch from another tree in one click | Same as Smart Match, multiplied | Very high: do not use |
| **Theory of Family Relativity** | Chains trees and records to explain a DNA match | Hypothesis built on unverified links | High: every link needs checking |
| **Ancestry / FamilySearch hints** | Same principle as above | Same | Same |
| **GEDBAS, Geni, WikiTree, OFB** | Compiled data | Derivative; quality varies by compiler; OFBs often cite the Kirchenbuch | Medium |

The user interface and labels on these sites change. If the user describes a
screen that does not fit this table, ask what they see rather than guessing.

Two errors are possible, and they are not symmetric:

- **False positive** (confirming a wrong match) grafts a foreign lineage into
  the tree, and every generation above it is then wrong. It propagates to other
  users through the same matching system. Expensive, hard to detect later.
- **False negative** (rejecting a right match) loses a lead. On MyHeritage a
  rejected match leaves the default view and is only reachable through the
  "Rejected" status filter, so a wrong rejection is easy to forget — reject
  only on a documented hard conflict, otherwise leave pending.

Hence the asymmetry in the rules: **confirm strictly, reject strictly, and
leave everything in between pending with a note.**

MyHeritage mechanics that matter here (per its own knowledge base; verify
against the current UI):

- Matches carry a status: Pending, New, Confirmed, Rejected — all filterable.
- After confirming, a separate page offers to **extract** information into the
  tree. Extraction can be done manually field by field, also later.
- **"Quick Save"** copies *everything new* from the match into the tree in one
  step and attaches a citation that points at the match, not at a record.
  Never use it: it is a bulk import that looks sourced.
- The default sort is by **"Value Add"** — how much new data a match would
  bring. That puts the matches with the most unverified content first; it is
  not a measure of correctness.
- Record Matches can be filtered by a confidence level. Use it to prioritise
  review, not as a substitute for it.

## 2. Procedure

### Step 0 — Fix your own anchor

Before looking at the other tree, state what is *belegt* about the person on
the user's side, each with its source. If the user's own profile is unsourced,
the comparison is tree-vs-tree hearsay; say so and switch the task to "find a
record for our own person first".

### Step 1 — Inventory the claim

From the matching profile, list every asserted fact and note for each: is a
source cited? Is it an original record, an index, or another tree? Is an image
attached? "Source: MyHeritage Family Trees", "Ancestry Family Trees", "Geni
World Family Tree" or "Smart Match" are *not* sources — they are pointers to
more trees.

### Step 2 — Trace dependency (Abhängigkeit)

When several trees match: check whether they share the same errors, the same
odd spellings, the same estimated dates ("ca. 1790"), the same photo. Shared
idiosyncrasies mean a common origin; count them as **one** witness. Try to find
the earliest/most documented tree and contact its owner for the source if none
is given.

### Step 3 — Identifier matrix

Compare the two profiles identifier by identifier. For each, record: value A,
value B, source behind each, and a rating:

- **＝ übereinstimmend / concordant** (within the tolerance below)
- **≈ vereinbar / compatible** (not contradictory, not confirming — e.g. one
  side empty, or only year vs. full date)
- **≠ Konflikt / conflict**
- **∅ fehlt / missing on both sides**

Identifiers, roughly in descending discriminating power for German research:

1. Parents' full names (incl. mother's maiden name)
2. Spouse's full name + marriage date/place
3. Exact birth/baptism date and **parish/Standesamt**, not just "Germany"
4. Death/burial date and place, age at death
5. Children's names with dates (a set of 3+ matching children is strong)
6. Confession (kath./ev.-luth./ev.-ref./jüd./mennonit.)
7. Occupation or status (Ackerer, Tagelöhner, Schneidermeister, Kötter)
8. Hofname / house name / "genannt" name; street address in towns
9. Godparents and witnesses (FAN: friends, associates, neighbours)
10. Siblings
11. Given names incl. Rufname; surname incl. variants

Name + birth year are **necessary, never sufficient**. A single, common-name
match on name and year is the base case for a false positive.

Tolerances — what still counts as concordant:

- Baptism up to a few days after birth; burial a few days after death. Check
  which event each tree actually recorded before calling a 2-day gap a conflict.
- Ages at death and in census-like lists are approximate (±2–3 years, more for
  the old); a birth year *computed* from an age is weak.
- Spelling is not an identifier before the late 19th century
  (Schmitz/Schmidt/Schmits; Meyer/Meier/Maier; Latin Joannes/Johann).
  Different spelling is never a conflict by itself; identical spelling is never
  a confirmation by itself.
- Place may be recorded as hamlet, parish, Bürgermeisterei, or district town.
  Resolve via GOV / Meyers Gazetteer before rating. Same name ≠ same place
  (dozens of Neustadt, Hausen, Kirchheim, Neuenkirchen).

### Step 4 — Hard conflicts (K.-o.-Kriterien)

Any one of these, if both sides rest on a reliable source, means **widerlegt**
unless explained in writing:

- Different documented parents
- Still alive / having children / marrying after the other profile's documented
  death; born after own marriage or own child
- Documented in two distant places at the same time
- Different confession with no conversion or mixed-marriage record
- Mother under ~15 or over ~50 at a child's birth; father under ~15; child
  born more than ~9 months after father's death
- Two children of the same mother less than ~9 months apart (not twins)
- Spouse sets that cannot be sequenced (overlapping marriages)

If only the *other tree's unsourced claim* conflicts with the user's sourced
fact, the profile may still be the same person with a bad date on the other
side. That is "möglich, their data unreliable" — leave pending, do not import.

### Step 5 — Actively look for the namesake (Gegenprobe)

Assume a second person of the same name existed and try to find them. This is
the step that prevents most false positives:

- Search the parish's baptisms ±10 years for other children of the same name;
  include neighbouring parishes and the other confession's parish.
- Check for a same-named sibling who died young (the name was routinely reused
  for the next child — Nachbenennung).
- Check cousins: brothers frequently each named a son after the grandfather, so
  same-named first cousins of similar age in one village are normal.
- Follow each candidate forward (marriage, children, burial) until all but one
  are eliminated — by early death, different spouse, different farm.
- Two same-named people appearing **in the same record or list** (both as
  godparents, two households in one tax list or address book) are proof of
  distinct persons — never merge across that.

If a candidate cannot be eliminated, the verdict is at most **möglich**.

### Step 6 — Go to the record

At least one **original or image-of-original record examined by the user or
you** must tie the identity together — typically the marriage entry naming the
parents, or a baptism plus a burial with age and spouse. Index entries and
transcriptions are finding aids; fetch the image (Archion, Matricula,
FamilySearch, Landesarchiv) where one exists.

### Step 7 — Verdict and action

| Verdict | Condition | MyHeritage action | Data transfer |
|---------|-----------|-------------------|---------------|
| **belegt** | No hard conflict; ≥ 3 concordant *independent* identifiers from the top-9 list beyond name/year, at least one of them a relationship (parents or spouse); namesake search done; ≥ 1 original record examined | Confirm | Only verified facts, field by field, each cited to the underlying record |
| **wahrscheinlich** | As above, but one named gap (e.g. namesake search incomplete, or record seen only as index) | Leave pending | None yet |
| **möglich** | Compatible, but < 3 discriminating identifiers or an uneliminated namesake | Leave pending | None |
| **ungeklärt** | Too little data, or soft conflicts unexplained | Leave pending | None |
| **widerlegt** | Documented hard conflict | Reject; **document**: conflict, sources, date | None; note the namesake so the hint is recognised next time |

The thresholds are a floor for discipline, not a score to game. Three weak
identifiers copied from one tree are one identifier. When in doubt, downgrade.

Only rejections and overrides are written down (template in
`assets/vorlagen.md`); pending matches get no note. If the user confirms
below the threshold, follow "Überstimmen" in SKILL.md: log the missing
conditions, status prefix at most `[wahrscheinlich]`, `Nachprüfen:` with the
deciding record.

Work the backlog by closeness of relationship (direct ancestors first, one
generation at a time), not in the site's default order.

Never: confirm in bulk; accept "extract all info"; let a match overwrite an
existing sourced value; adopt a photo, parents or a whole branch because the
match on the focus person was good — **each attached relative is a separate
identity question** and gets its own pass through this protocol.

## 3. Output format

Use this structure for every evaluation (German labels if the user writes
German). The verdict comes first, the matrix stays complete, and the reply
ends with exactly one next step (`ausgabeform.md`):

```
SMART-MATCH-PRÜFUNG / MATCH EVALUATION
URTEIL / VERDICT: belegt | wahrscheinlich | möglich | ungeklärt | widerlegt
Aktion in MyHeritage: bestätigen | offen lassen | ablehnen
Grund / deciding reason: <one sentence: the identifier or conflict that decides, with its source>

Person (eigener Baum / own tree): <name, *date place, ID>
Gegenprofil / matched profile:    <name, tree/site, owner, URL or ID>
Anker / anchor facts (belegt):    <fact — source>

Matrix
| Merkmal / identifier | Eigener Baum (Quelle) | Gegenprofil (Quelle) | ＝ ≈ ≠ ∅ |

Harte Konflikte / hard conflicts:  <none | list — every one, never shortened>
Weiche Abweichungen / soft:        <list with explanation>
Abhängigkeit / dependency:         <n trees → m independent origins>
Gegenprobe Namensvetter / namesake search: <done: scope, result | not done>
Geprüfte Originalquelle / record examined: <citation | none>

Begründung / reasoning: <2–5 sentences, only what the lines above do not already say>
Übernehmen / take over: <explicit list of fields, or "nichts / nothing">
Nächste Quellen / next sources: <ranked, at most five shown, with repository and signature if known>
Nächster Schritt / next step: <exactly one, precise enough to start now>
```

If information needed for the matrix is missing, ask for it or mark ∅ — never
fill a cell from assumption.

## 4. Typical false-positive patterns in German research

- **Emigrant graft.** An overseas tree attaches an emigrant ancestor to the
  first German baptism with the right name and decade. Demand a link in the
  record: emigration file, passenger list with last residence, church record
  abroad naming the German parish, or matching family group.
- **Rufname confusion.** "Johann Heinrich" (called Heinrich) matched to brother
  "Johann Wilhelm" because both are indexed as "Johann".
- **Nachbenennung.** Baptism of the child who died as an infant attached to the
  later sibling of the same name — makes the person a few years "older".
- **Hofname/Genannt-Namen** (Westfalen, Lippe, parts of Niedersachsen). The man
  who married onto the farm took the farm's name; children may appear under
  either. Matches on surname alone connect unrelated holders of one farm, or
  miss the real father. See `regionale-besonderheiten.md`.
- **Patronymics** (Ostfriesland, Schleswig, parts of the Lower Rhine before
  ~1811). "Jan Harms" is Jan, son of Harm — not a member of a Harms family.
- **Parish confusion.** Same village name in different regions; or the right
  village but the family belonged to the other confession's parish elsewhere.
- **Estimated dates turned into facts.** "Born 1790" derived from age at death,
  then matched "exactly" to a baptism in 1790. Circular.
- **Second marriages.** Children of the first wife assigned to the second, or
  two same-named men merged because both had a wife called Anna Maria.
- **Noble/medieval overreach.** Lines running back before the start of the
  local Kirchenbuch (often after 1648) without charters, tax lists or court
  records behind them are unproven by default.
- **Index errors.** Kurrent misread (u/n, e/n, long s/f, K/R), Latin genitive
  taken as surname, godparent indexed as parent.
- **Ahnenpass/Ariernachweis.** Compiled 1933–45 under pressure, sometimes
  adjusted; certified extracts are useful, the summary booklet is derivative.

## 5. Duplicates within the user's own tree

Merging two profiles is the same identity question. Run the matrix, and before
merging export a GEDCOM backup and note which sources belonged to which
profile. A merge is hard to undo; if the verdict is below *belegt*, link the
profiles with a note instead.

## 6. Rückbau / Taking a wrong link out of the tree

Earlier confirmations, Quick Saves and imports may already sit in the tree.
`scripts/gedcom_plausi.py` lists the candidates: facts whose only source is
another tree, and chronological impossibilities. A candidate is a reason to
check, not a reason to delete. Removal follows the rule for any weeding —
evaluate, document, keep it reversible.

1. **Export first.** Pull a dated GEDCOM export before touching anything.
   It is the record of what was there, not an undo: a re-import makes a new
   tree and loses detail.
2. **One link at a time**, nearest generation first, each through the
   procedure in section 2. Never remove a branch because its top looks
   wrong: find the lowest link that does not hold. Everything above hangs
   on that link.
3. **The verdict decides the action:**

   | Verdict on the link | Action |
   |---------------------|--------|
   | belegt · wahrscheinlich | Keep. Add the missing citation and the status prefix. |
   | möglich · ungeklärt | Does not belong in the tree. Detach the link and keep the branch as a hypothesis — or, if the user decides to keep it, mark it like an override: status prefix and `Nachprüfen:`. |
   | widerlegt | Detach the link. What happens to the detached persons is the user's decision. |

4. **Detach before delete.** Removing a connection keeps the profiles and
   their sources; deleting persons destroys them. In MyHeritage: person
   card → More → Remove connection, then "From parents" or "From partner";
   a child is detached from its own card, not from the parent's. Delete
   only what the user decides to delete, and never in bulk.
5. **Log it** like a rejected match: which link, the verdict, the conflict
   or the missing evidence, the date, and the export file that still holds
   the branch. Keep the namesake's data with the hypotheses — the next
   Smart Match will offer the same branch again.
6. Afterwards run the plausibility check on a fresh export and compare the
   two reports.
