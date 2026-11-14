# DNA-Grundlagen (MyHeritage) / DNA basics

Scope: enough to classify a DNA match as evidence and to keep it from
overriding documents. Not a guide to genetic genealogy. MyHeritage's features
and thresholds change — describe what the user actually sees, and check the
MyHeritage knowledge base before quoting a number.

## 1. What a DNA match is as evidence

- A match shows that two people **share DNA segments**; it says nothing by
  itself about *which* ancestors they share or through which line.
- In this skill's terms it is **indirect evidence**: it needs a documented
  tree on both sides before it bears on a research question.
- The amount shared (centimorgans, cM) fits **several relationships at
  once**. Half-siblings, grandparent/grandchild, uncle/niece and double first
  cousins overlap; beyond second cousins the ranges overlap widely. Use a
  shared-cM table (e.g. the Shared cM Project) to list *all* relationships
  that fit, then let documents choose.
- DNA can **disprove** a documented line (expected close relative shares
  nothing) more firmly than it can prove a distant one.
- **No shared DNA proves nothing beyond about third cousins**: distant
  cousins often share no detectable segment.

## 2. MyHeritage tools and how to treat them

| Tool | What it does | Treat as |
|------|--------------|----------|
| **DNA Match list** (shared cM, number of segments, largest segment, estimated relationships) | Raw comparison | Starting data. The estimated relationship is a range, not a finding |
| **Shared matches** | People who match both of you | Hint at which side of the family a match belongs to |
| **Theory of Family Relativity** | Chains *trees and records* into a path explaining the match | A **hypothesis built from other people's trees**. Every link is a separate Smart-Match-type claim → run each through `smart-match-pruefung.md`. The DNA is consistent with many paths; it does not validate this one |
| **AutoClusters** | Groups matches that also match each other | Clusters usually point to one ancestral couple; which couple must come from documents |
| **Chromosome Browser** | Shows the shared segments; triangulation where three people share the same segment | Supports a common ancestor for that segment — still does not name the ancestor |
| **Ethnicity estimate / Genetic Groups** | Statistical comparison with reference populations | **Not evidence** for any individual ancestor or place. Never enter it as a fact |

## 3. Typical wrong conclusions

- **"We share DNA and both have a Schmitz from Neuss, so that's the link."**
  The shared ancestor may be on a completely different line. Check all lines
  of both trees to the depth the cM value implies.
- **Endogamy and pedigree collapse (Ahnenschwund)**: in small villages and
  closed communities (Mennonites, Jewish communities, Danube-Swabian
  villages) people are related several ways. Shared cM is inflated and
  suggests closer relationships than exist. Many small segments rather than
  few large ones is the warning sign.
- **Small segments**: matches resting only on short segments are often false
  positives. Give weight to the largest segment, not the total.
- **Trusting the theory because it is "confirmed by DNA"**: the DNA confirms
  relatedness, the path is conjecture.
- **Circular proof**: tree built from Smart Matches → Theory of Family
  Relativity built from those trees → theory cited as confirmation of the
  Smart Matches.
- **Uploaded data from other companies** was tested on different chips;
  comparison partly rests on imputed data and is less reliable for small
  segments *(check MyHeritage's current description)*.

## 4. Procedure for a DNA lead

1. Record: match name, shared cM, segments, largest segment, date, and which
   known relatives are shared matches.
2. List every relationship the cM value allows.
3. Place the match on a side of the family using shared matches with known
   relatives (test the oldest living generation where possible — they carry
   more of the relevant DNA).
4. Compare trees; identify candidate common ancestors on **all** lines.
5. Document both descents from the candidate couple with records, each link
   to the usual standard.
6. Verdict uses the normal status vocabulary. DNA alone never yields
   *belegt* for a specific ancestor; documents plus consistent DNA can.

## 5. Linking matches, clusters and segments to the tree

Master copy is a **local table** built from the files the user downloads from
MyHeritage (match list, shared segments); a chromosome-mapping tool such as
DNA Painter is fed from that table for display, never the other way round.

Three linked tables (CSV or Markdown, in the user's storage):

**matches** — one row per match worth working on

| match_id | Name | cM gesamt | Segmente | größtes Segment | Baum vorhanden | gemeinsame Matches (bekannte Verwandte) | Cluster | Familienseite | Ahnenpaar (Hypothese) | Status | Beleg | zuletzt geprüft |

**segments** — one row per shared segment

| match_id | Chromosom | Start | Ende | cM | SNPs | Ahnenpaar | Seite (v/m) | Status | Grundlage |

**clusters** — one row per cluster

| Cluster | Quelle (Lauf, Datum, Schwellen) | Mitglieder | Ahnenpaar | Status | Grundlage |

Rules:

1. **Person in the tree first.** A match is linked to a tree person only
   when the match's descent from the common ancestors is documented to the
   usual standard. Until then `Ahnenpaar` is a hypothesis with status.
2. **Cluster → couple** needs at least **two members whose descent from that
   couple is documented**, on different child lines where possible. One
   documented member makes a cluster "möglich".
3. **Segment → couple** needs **triangulation**: at least three people, not
   all from one nuclear family, who share the *same* segment and are each
   documented descendants of the couple. Two people sharing a segment with
   you is not triangulation unless they also share it with each other.
4. Assign the segment to the **couple**, not to one spouse, unless a match
   descends from only one of them (other marriage).
5. Ignore very small segments for assignment; they are frequently false.
   Record the threshold used in `Grundlage`.
6. In endogamous or pedigree-collapse lines a segment can come from more
   than one couple — mark it `mehrdeutig` rather than forcing it.
7. Status vocabulary as everywhere; a segment assignment is at most
   *wahrscheinlich* unless rule 3 is met.
8. Into the tree goes the **documented descent**, cited to records. The DNA
   observation goes into the note of the relationship as supporting,
   indirect evidence: match, cM, segment, date, table reference.
9. Re-running AutoClusters changes cluster numbering: record run date and
   settings, and key clusters by their members, not by number.
10. Raw DNA files and match lists stay in the user's storage; nothing from
    them is pasted into public trees.

## 6. Unexpected results

DNA can reveal unknown parentage, half-siblings or adoptions. Report such a
finding plainly and only as far as the data supports it (list the
relationships that fit, say what would distinguish them), and leave to the
user whether and how to pursue or share it.
