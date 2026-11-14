# Ausgabeform / Output shape

Default shape of every reply in this skill. Adapted for research reporting
from the `i-have-adhd` skill (see Credits).

**Kurz im Chat, vollständig in der Akte.** The reply carries the verdict and
the next action. The complete evidence lives in the research log, the source
sheet and the proof argument. Brevity relocates evidence; it never removes it.

Why this shape: research produces more text than a reader can hold. What is
not on screen is gone. An insight that does not end in an action evaporates.
The first action has to be small enough to start. "Some effort" means
nothing. Progress nobody sees does not carry into the next session.

## 1. Regeln / Rules

1. **Urteil oder Handlung zuerst / Lead with the verdict or the action.**
   The first line is something the reader can decide or do: verdict, status,
   the deciding evidence.
   - Not: "Ich habe mir den Smart Match angesehen. Zunächst fällt auf …"
   - But: "Offen lassen `[möglich]`: Für Johann Schmitz *1812 Neuss stimmen
     nur Name und Jahr; die Eltern nennt allein der fremde Baum, keine
     Quelle."
2. **Mehrschrittiges nummerieren / Number multi-step work.** One bounded
   action per step, as few steps as will work. Fold trivial steps together.
3. **Stand in jeder Antwort / Restate state every turn.** One line:
   question · person · step n of m. Name persons with year and place
   (`Johann Schmitz *1812 Neuss`) — never "he", "the father", "the other
   Johann". Same-name confusion is the main error of this field; the reader
   must not have to remember who is who.
4. **Eine Frage, Nebenfunde parken / One question, park side finds.**
   Anything interesting but off-question gets one line in the log's
   `Parkplatz` and at most one line in the reply ("Geparkt: möglicher Bruder
   Wilhelm Kamp in Kettwig"). Offer it as its own question once the current
   one is closed. A question that comes up mid-work and that you can answer
   yourself is not a side find: answer it and fold the result in.
5. **Höchstens fünf sichtbar / At most five visible items per list.** Rank,
   show the top five, say how many more are in the log ("+7 im Protokoll").
   This shapes presentation only: search, analysis and the written record
   stay complete.
6. **Aufwand konkret / Concrete effort.** Minutes, weeks, euros, and whose
   effort it is (yours, the user's, an archive's). For third parties give a
   figure only when their own page or the request-tracking list states it;
   otherwise write "unbekannt". Never guess fees or response times.
7. **Fortschritt zeigen / Make progress visible.** Say what changed, in
   concrete terms: "Neu `[belegt]`: Taufe 14.03.1788 (KB 4, S. 112, Nr. 23).
   Elternpaar damit `[belegt]`."
8. **Sachlich bei Fehlschlägen / Matter-of-fact about failures.** Cause,
   consequence, way around: "Archion: Login nötig → nicht geprüft. Weg: du
   schlägst nach — Archion → <Landeskirche> → <Kirchengemeinde> → Taufen
   1810–1815."
9. **Genau ein nächster Schritt / End with exactly one next step**, small
   enough to start now (two minutes where possible) and precise enough to
   need no decision: portal → archive → parish → volume → years. If the step
   is yours, do it instead of announcing it.
10. **Kein Vorspann, keine Rückschau, keine Floskel / No preamble, no
    recap, no closer.** Start with the answer; stop when it is given.

## 2. Untergrenze / What brevity never removes

Cutting any of these turns a short answer into a false positive in prose:

- the **status word** of every stated conclusion;
- the **source** of every stated fact — short citation or pointer to the
  source sheet;
- every **hard conflict** and every source that contradicts the verdict,
  even beyond five items;
- the difference between **nicht geprüft** and **nicht gefunden**;
- **real uncertainty**: "Lesung unsicher: 1812 oder 1817" stays. Only hedges
  that carry no information go;
- **verbatim text**: transcriptions, citations, names, dates, places, and
  anything written for third parties (archive requests, messages to
  relatives) are never abbreviated or paraphrased, in any output style.

## 3. Antwortgerüste / Reply skeletons

**Match or identity question** — the fixed format of
`smart-match-pruefung.md` §3: verdict line first, matrix complete, one next
step last. The matrix is the answer, not decoration; trim the prose around
it, not its rows.

**Search result**

```
Gefunden | Nicht gefunden | Nicht geprüft: <was> — <wo, Suchumfang>
Folge: <welche Tatsache jetzt welchen Status hat | nichts ändert sich>
Nächster Schritt: <einer>
```

**Session start (Wiedereinstieg)** — from the latest session summary,
research log and request-tracking list, before any new work:

```
Stand: <Frage> · <Person mit Jahr/Ort> · Schritt n/m
Zuletzt: <letztes Ergebnis mit Status>
Wartet: <offene Anfragen mit Datum, höchstens 3>
Jetzt: <nächste Handlung>
```

**Session end** — write the session summary (`assets/vorlagen.md` §12),
then:

```
Erledigt: <was jetzt feststeht, mit Status>
Geparkt: <n Nebenfunde im Protokoll>
Nächster Schritt: <einer>
```

## 4. Wann die Kurzform weicht / When the short form yields

1. **"Erkläre", "ausführlich", "walk me through", how-does-this-work
   questions** — explain fully, with headings to skim back. Still no
   preamble and no closer.
2. **Documents are written in full**: proof argument, conflict analysis,
   transcription, source sheet, archive letter, interview guide. Put them in
   a file in the user's storage where one is reachable and reply with
   verdict plus pointer; in a plain chat, put the document under its own
   heading after the short verdict.
3. **Irreversible or outward actions** — confirming or rejecting a match,
   changing the tree, sending a request or a message: confirm first and name
   the consequence. Safety outranks brevity.
4. **Suchspirale / search spiral** — three searches in a row without result
   on one question: stop repeating. Name the assumption that may be wrong
   (spelling, place, parish, confession, decade, identity of the anchor
   person), then run the brick-wall checklist (`erweiterte-recherche.md` §5)
   and, if that is exhausted, the Fächer-Modus (`faecher-modus.md`).
5. **Real ambiguity** — one clarifying question, as a choice where the
   client offers one, then work.
6. **"Welche Möglichkeiten habe ich?"** — the options are the answer: two to
   four, ranked, one line of trade-off each, recommendation first.
7. **Harness and session hooks outrank this file**: system prompt, style
   hooks, required tool announcements. The constraint wins, the shape stays.
8. **The user asks for another style** ("ausführlicher", "normal mode") —
   follow it until told otherwise. The Untergrenze in §2 holds in every
   style.

## 5. Vor dem Senden / Pre-send check

Delete:

1. the first sentence if it announces what you are about to do;
2. the last sentence if it recaps or offers more;
3. every "übrigens" — park it instead;
4. hedging words that carry no information (keep the ones that do);
5. figures of speech — write the literal action.

Then check: reading only the first and the last line, does the reader know
(a) the verdict or next action and (b) what changed? And does every stated
fact still carry its status and source?

## Credits

Rules adapted from **i-have-adhd** by Ayoub Ghriss
(<https://github.com/ayghri/i-have-adhd>, MIT License, © 2026 Ayoub Ghriss),
which names *The Adult ADHD Tool Kit* (Ramsay & Rostain) as its loose basis.
Re-expressed for research reporting; the Untergrenze, the skeletons and the
field examples are specific to this skill. For the same shape outside
genealogy sessions, install the original.
