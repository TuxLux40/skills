# Vorlagen / Templates (DE + EN)

Copy, fill, keep. Leave unknown fields as `unbekannt` / `unknown` — never
fill from assumption.

## 1. Forschungsprotokoll / Research log

```markdown
# Forschungsprotokoll – <Forschungsfrage in einem Satz>
Person: <Name, ID>   Stand: <JJJJ-MM-TT>

## Ausgangslage (bekannt, mit Quelle und Status)
- <Tatsache> — <Quelle> — <belegt|wahrscheinlich|möglich|ungeklärt>

## Suchen
| Datum | Quelle (Archiv, Bestand, Signatur, Jahre) | Suchumfang (Namen, Varianten, Seiten) | Ergebnis | Bewertung | Folgeschritt |
|-------|-------------------------------------------|----------------------------------------|----------|-----------|--------------|
|       |                                           |                                        | gefunden / nicht gefunden / Lücke / unleserlich | | |

## Befunde
- <Befund> — <Zitat> — Status: <…>

## Widersprüche
- <Wert A (Quelle)> ↔ <Wert B (Quelle)> — Erklärung: <… | offen>

## Verworfene Hypothesen
- <Hypothese> — widerlegt durch <Quelle>, weil <…>

## Parkplatz (Nebenfunde, nicht zu dieser Frage)
- <Fund> — <Quelle> — eigene Frage wert: <ja | nein>

## Nächste Schritte
1. <Quelle, Archiv, was genau prüfen>   ← der eine nächste Schritt
```

```markdown
# Research log – <research question in one sentence>
Person: <name, ID>   As of: <YYYY-MM-DD>

## Starting point (known, with source and status)
- <fact> — <source> — <proven|probable|possible|unresolved>

## Searches
| Date | Source (repository, fonds, call no., years) | Scope (names, variants, pages) | Result | Assessment | Next step |
|------|----------------------------------------------|--------------------------------|--------|------------|-----------|
|      |                                              |                                | found / not found / gap / illegible | | |

## Findings
- <finding> — <citation> — status: <…>

## Conflicts
- <value A (source)> ↔ <value B (source)> — explanation: <… | open>

## Rejected hypotheses
- <hypothesis> — disproven by <source> because <…>

## Parked (side finds, off this question)
- <find> — <source> — worth its own question: <yes | no>

## Next steps
1. <source, repository, what exactly to check>   ← the one next step
```

## 2. Quellenblatt / Source record sheet

```markdown
# <JJJJ-MM-TT> <Ereignis> <NACHNAME, Vorname> – <Ort>

**Zitat / Citation:** <Archiv, Bestand, Signatur, Titel, S./Bl., Nr.>
**Zugriff / Access:** <Portal, Permalink/Bildnr., eingesehen am | Original | Kopie vom Archiv>
**Art / Type:** Original | Zweitschrift | Abschrift | Index | Kompilation
**Sprache, Schrift / Language, script:** <Deutsch/Latein/Französisch; Kurrent/…>
**Datei / File:** <Dateiname des Masters>

## Transkription (buchstabengetreu / verbatim)
> <Text; [?] unsicher, […] unleserlich, Auflösungen in [eckigen Klammern]>
Gelesen von / read by: <Person | maschinell, ungeprüft / machine, unchecked>

## Übersetzung / Normalisierte Lesung
<…>

## Extrahierte Angaben / Extracted information
| Person | Rolle / role | Angabe / statement | Information (primär/sekundär/unbestimmt) |
|--------|--------------|--------------------|------------------------------------------|

**Informant / Anzeigender:** <Name, Verhältnis | nicht genannt>
**Äußere Kritik:** <Zustand, Nachträge, Reihenfolge, Hand>
**Innere Kritik:** <Nähe zum Ereignis, Motiv, Plausibilität>
**Belegt für Forschungsfrage / Evidence for question:** <direkt | indirekt | negativ> — <welche Frage>
```

## 3. Smart-Match-Prüfung / Match evaluation

```markdown
# Match-Prüfung <JJJJ-MM-TT> – <Name, ID>

**URTEIL / VERDICT:** belegt | wahrscheinlich | möglich | ungeklärt | widerlegt
**Aktion in MyHeritage:** bestätigen | offen lassen | ablehnen
**Grund / deciding reason:** <ein Satz: das entscheidende Merkmal oder der Konflikt, mit Quelle>

Eigenes Profil / own profile: <Name, *Datum Ort, ID>
Gegenprofil / matched profile: <Name, Seite, Baum, Verwalter, URL/ID>
Hinweistyp / hint type: Smart Match | Record Match | Instant Discovery | Theory | anderer

## Anker (eigener Baum, belegt) / Anchor facts
- <Tatsache> — <Quelle>

## Matrix
| Merkmal / identifier | Eigener Baum (Quelle) | Gegenprofil (Quelle) | ＝ ≈ ≠ ∅ |
|----------------------|-----------------------|----------------------|---------|
| Eltern / parents | | | |
| Ehepartner, Heirat / spouse, marriage | | | |
| Geburt/Taufe: Datum, Pfarrei/StA | | | |
| Tod/Begräbnis | | | |
| Kinder / children | | | |
| Konfession | | | |
| Beruf/Stand / occupation | | | |
| Hof-/Hausname, Adresse | | | |
| Paten, Zeugen / godparents, witnesses | | | |
| Geschwister / siblings | | | |
| Namen inkl. Rufname, Varianten | | | |

Harte Konflikte / hard conflicts: <keine | …>
Weiche Abweichungen / soft discrepancies: <… + Erklärung>
Abhängigkeit / dependency: <n Bäume → m unabhängige Ursprünge>
Gegenprobe Namensvetter / namesake search: <Umfang, Ergebnis | nicht durchgeführt>
Geprüfte Originalquelle / record examined: <Zitat | keine>

**Begründung / reasoning:** <…>
**Übernehmen / take over:** <Feldliste mit jeweiliger Originalquelle | nichts>
**Nächste Quellen / next sources:** <nach Rang, höchstens fünf>
**Nächster Schritt / next step:** <genau einer>
```

### Abgelehnter Match / Rejected match (Kurzform)

```markdown
# Abgelehnt <JJJJ-MM-TT> – <eigene Person, ID> ≠ <Gegenprofil, Baum, Verwalter>
Konflikt / conflict: <harter Konflikt in einem Satz>
Belege / sources: <Zitat eigene Seite> ↔ <Zitat/Angabe Gegenseite>
Namensvetter / namesake: <wer das Gegenprofil vermutlich ist>
```

### Überstimmung / Override

```markdown
# Überstimmt <JJJJ-MM-TT> – <Person, ID> ← <Gegenprofil, Baum>
Urteil des Skills / verdict: <möglich | ungeklärt | wahrscheinlich>
Nicht erfüllt / not met: <z. B. keine Originalquelle, Namensvetter-Suche offen>
Grund des Nutzers / user's reason: <… | nicht genannt>
Übernommen / adopted: <Felder> — Status: [wahrscheinlich] | [möglich]
Nachprüfen: <Quelle, Archiv, Signatur falls bekannt>
```

## 4. Widerspruchsanalyse / Conflict analysis

```markdown
| | Wert A | Wert B |
|---|--------|--------|
| Angabe / statement | | |
| Zitat / citation | | |
| Quelle: Original/Derivat/Kompilation | | |
| Information: primär/sekundär/unbestimmt | | |
| Informant, zeitl. Abstand / informant, time lag | | |
| Motiv zur Abweichung? / motive? | | |

Erklärung / explanation: <…>
Bevorzugt / preferred: <A | B | keiner> — weil / because <…>
Status: <…>
```

## 5. Belegführung / Proof argument

```markdown
# <Behauptung / claim, e.g. "Anna Maria Schmitz (oo 1843) war Tochter von …">

Forschungsfrage / question: <…>
Recherche-Umfang / scope of research: <Quellen geprüft; nicht verfügbare Quellen>
Belege / evidence: <nummeriert, je mit Zitat und Einstufung>
Auswertung / analysis: <Abgleich, Zeitleiste, Familiengruppe, FAN>
Widersprüche / conflicts: <jeweils mit Auflösung>
Alternativen / alternatives considered: <Namensvetter u. a. – warum ausgeschlossen>
Schluss / conclusion: <Satz> — Status: <belegt | wahrscheinlich …>
Offen / remaining gaps: <…>
```

## 6. Archivanfrage / Request to an archive or Standesamt

```text
Betreff: Familiengeschichtliche Anfrage – <Registerart> <Name>, <Ort>, <Jahr/Zeitraum>

Sehr geehrte Damen und Herren,

im Rahmen meiner familiengeschichtlichen Forschung bitte ich um eine Kopie
des vollständigen Registereintrags (einschließlich Randvermerken) zu:

  Name, alle Vornamen:   <…>
  Ereignis:              <Geburt | Heirat | Tod>
  Datum / Zeitraum:      <… (gesichert | geschätzt aus …)>
  Ort / Standesamt / Pfarrei, Konfession: <…>
  Eltern / Ehepartner:   <…>
  Beruf, Wohnung:        <…>
  Mein Verwandtschaftsverhältnis: <z. B. Urenkel in gerader Linie>

Gesichert ist: <…>. Vermutet ist: <…>.
Falls vorhanden, bitte ich auch um Auskunft zu Sammelakten sowie um Angabe
von Signatur und Seite/Nummer. Bitte nennen Sie mir vorab die
voraussichtlichen Gebühren, falls diese <Betrag> € überschreiten.

Mit freundlichen Grüßen
<Name, Anschrift, E-Mail>
```

```text
Subject: Family history enquiry – <record type> <name>, <place>, <year/period>

Dear Sir or Madam,

For my family history research I would like to request a copy of the complete
register entry (including marginal notes) for:

  Name, all given names: <…>
  Event:                 <birth | marriage | death>
  Date / period:         <… (documented | estimated from …)>
  Place / registry office / parish, denomination: <…>
  Parents / spouse:      <…>
  Occupation, residence: <…>
  My relationship:       <e.g. great-grandchild in direct line>

Documented: <…>. Assumed: <…>.
If supporting files (Sammelakten) survive, please let me know, and please
state the call number and page/entry number. Kindly inform me of the expected
fees in advance if they exceed € <amount>.

Yours faithfully,
<name, address, e-mail>
```

## 7. Nachricht an Baum-Verwalter / Message to a tree owner

```text
Guten Tag,
in Ihrem Stammbaum führen Sie <Name, *Jahr Ort>. Ich forsche zu einer
Person gleichen Namens und prüfe, ob es dieselbe ist. Mir liegt vor:
<Quelle, kurz>. Könnten Sie mir sagen, auf welcher Quelle Ihre Angabe
<Eltern | Geburtsdatum | …> beruht (Kirchenbuch/Standesamt, Signatur oder
Bild)? Gern teile ich meine Belege. Vielen Dank!
```

```text
Hello,
your tree includes <name, b. year place>. I am researching a person of the
same name and checking whether they are identical. I have: <source, brief>.
Could you tell me which source your <parents | birth date | …> is based on
(parish or civil register, call number or image)? Happy to share my
documentation in return. Thank you!
```

## 8. Interview

```markdown
# Interview <JJJJ-MM-TT> – <Name>, <Verhältnis>, <Ort>
Einwilligung / consent: Aufnahme <ja|nein>; Nutzung: <nur Familie | Veröffentlichung nach Rücksprache | …>
Dateien: <audio> · <transkript> · Transkript-Status: <maschinell, ungeprüft | geprüft am …>
Mitgebracht / prompts: <Fotos, Dokumente>

## Vorbereitung: offene Punkte im Baum, die diese Person klären könnte
- <Lücke/Widerspruch> — <Frage dazu, offen formuliert>

## Auswertung
| Aussage | Zeitmarke | Woher bekannt | Information (primär/sekundär) | Prüfbar durch | Status |
|---------|-----------|---------------|-------------------------------|---------------|--------|

## Neue Forschungsfragen
1. <Frage> — <Quelle, Stelle>

## Hinweise auf weitere Personen und Unterlagen
- <wen noch fragen, wer hat Papiere/Fotos>
```

## 9. Anfragenliste / Request tracking

```markdown
| Datum | Stelle | Betreff / Person | Weg | Aktenzeichen | Gebühr | Status | Antwort am | Ergebnis | Nächster Schritt |
|-------|--------|------------------|-----|--------------|--------|--------|------------|----------|------------------|
```
Status: entwurf · gesendet · eingangsbestätigung · rückfrage · beantwortet · negativ · keine antwort

Erinnerung / reminder:

```text
Sehr geehrte Damen und Herren,
am <Datum> habe ich Sie um <Gegenstand> zu <Person> gebeten (<Aktenzeichen,
falls vorhanden>). Darf ich höflich nach dem Stand fragen? Sollten weitere
Angaben oder Nachweise nötig sein, reiche ich sie gern nach.
Mit freundlichen Grüßen
```

```text
Dear Sir or Madam,
on <date> I asked for <item> concerning <person> (<reference, if any>). May I
kindly ask about the status? If further details or proof are needed, I will
gladly supply them.
Yours faithfully,
```

## 10. Erstkontakt zu Verwandten / First contact with a relative or DNA match

```text
Guten Tag <Name>,
ich heiße <Name> und forsche zu meiner Familie. Nach meinen Unterlagen sind
wir beide Nachkommen von <Ahnenpaar, Lebensdaten, Ort> – <bei DNA: MyHeritage
zeigt uns als Match mit rund … cM>. Ich habe dazu <Belege, kurz> und teile sie
gern. Wissen Sie, <eine konkrete Frage>?
Über eine Antwort freue ich mich; wenn Sie keinen Kontakt wünschen, ist das
selbstverständlich in Ordnung.
```

```text
Hello <name>,
my name is <name> and I am researching my family. According to my records we
both descend from <ancestral couple, dates, place> – <for DNA: MyHeritage
shows us as a match of about … cM>. I have <documents, brief> and am happy to
share them. Do you happen to know <one concrete question>?
I would be glad to hear from you; if you would rather not be in touch, that
is of course fine.
```

## 11. DNA-Tabellen / DNA tables

```markdown
matches:  | match_id | Name | cM gesamt | Segmente | größtes Segment | Baum vorhanden | gemeinsame Matches | Cluster | Familienseite | Ahnenpaar (Hypothese) | Status | Beleg | zuletzt geprüft |
segments: | match_id | Chromosom | Start | Ende | cM | SNPs | Ahnenpaar | Seite (v/m) | Status | Grundlage |
clusters: | Cluster | Quelle (Lauf, Datum, Schwellen) | Mitglieder | Ahnenpaar | Status | Grundlage |
```

## 12. Sitzungszusammenfassung für die Wissensbasis / Session summary for the KB

```markdown
# Genealogie-Sitzung <JJJJ-MM-TT>
Stand: <Frage> · <Person mit Jahr/Ort> · Schritt n/m
Forschungsfragen: <…>
Geprüfte Quellen: <Zitate; inkl. negativer Ergebnisse mit Suchumfang>
Ergebnisse: <Befund — Status>
Match-Entscheidungen: <Profil — Urteil — Aktion>
Offene Widersprüche: <…>
Verworfen: <Hypothese — Grund>
Geparkt: <Nebenfunde>
Wartet: <Anfrage — Stelle — gesendet am>
Nächster Schritt: <genau einer, sofort beginnbar>
Danach: <priorisiert>
Neue Dateien: <Dateinamen>
```

The `Stand`, `Wartet` and `Nächster Schritt` lines are what the next session
opens with (`references/ausgabeform.md` §3).

## 13. Fächer-Lauf / Divergent run

Record of one run of `references/faecher-modus.md`. Leads are not findings:
nothing here carries a status above `[möglich]`.

```markdown
# Fächer-Lauf <JJJJ-MM-TT> – <Forschungsfrage in einem Satz>
Anlass: <auf Zuruf | Sackgasse: was erschöpft ist>
Lauf: <n Rahmen × m Ansätze> · <isoliert | Ersatzlauf ohne Isolation>
Rahmen: <…>

## Lagebild (für alle Zweige gleich)
FRAGE:     <…>
PERSON:    <Name · * · ∞ · † — nur belegt/wahrscheinlich, je mit Kurzquelle>
UNBELEGT:  <was Baum, Überlieferung, fremde Bäume behaupten>
GEPRÜFT:   <Suchen mit Umfang und Ergebnis>
RAUM/ZEIT: <Pfarrei, Standesamt, Territorium, Konfession, Beruf, Stand>

## Shortlist
| # | Ansatz | T | M | N | Vorhersage (stimmt / stimmt nicht) | Erster Schritt |
|---|--------|---|---|---|-------------------------------------|----------------|
| ★ |        |   |   |   |                                     |                |

## Suchaufträge
### <Ansatz>
Hypothese: <…>
Vorhersage: <stimmt sie → Quelle zeigt X; stimmt sie nicht → Y; Lücken der Reihe geprüft: ja | nein>
Quelle & Zugang: <Bestand, Stelle, Portal/Anfrage, Jahre, Namensvarianten>
Tragende Annahme: <…>
Erster Schritt: <…>
Aufwand: <Zeit / Kosten | unbekannt>
Folgeansätze: <…>

## Fallen
| Ansatz | Grund |
|--------|-------|

## Vollständiger Fächer
### <Gruppe: zugrunde liegender Blickwinkel>
- <Ansatz> [T_ M_ N_] (<Rahmen>)

## Fernziele (T hoch, M niedrig)
- <Ansatz> — <was sich ändern müsste>

## Querfrage
<…>

## Nachtrag
- <Ansatz> → gesucht am <Datum>, Protokoll <Verweis>, Ergebnis <…>
```

```markdown
# Divergent run <YYYY-MM-DD> – <research question in one sentence>
Occasion: <on request | dead end: what is exhausted>
Run: <n frames × m leads> · <isolated | substitute run without isolation>
Frames: <…>

## Brief (identical for all branches)
QUESTION:   <…>
PERSON:     <name · * · ∞ · † — proven/probable only, each with short source>
UNPROVEN:   <what tree, family lore, other trees claim>
SEARCHED:   <searches with scope and result>
PLACE/TIME: <parish, register office, territory, confession, occupation, status>

## Shortlist
| # | Lead | T | M | N | Prediction (holds / does not hold) | First step |
|---|------|---|---|---|-------------------------------------|------------|
| ★ |      |   |   |   |                                     |            |

## Search orders
### <lead>
Hypothesis: <…>
Prediction: <if true → source shows X; if false → Y; gaps in the series checked: yes | no>
Source & access: <record group, holder, portal/request, years, name variants>
Load-bearing assumption: <…>
First step: <…>
Effort: <time / cost | unknown>
Follow-up leads: <…>

## Traps
| Lead | Reason |
|------|--------|

## Complete fan
### <group: underlying angle>
- <lead> [T_ M_ N_] (<frame>)

## Long shots (T high, M low)
- <lead> — <what would have to change>

## Reopening question
<…>

## Addendum
- <lead> → searched on <date>, log <reference>, result <…>
```

## 14. Personen-Netz / Person network (FAN table)

One row per person per record. Fill it from every captured record of the
family group, then run the connection scan (`references/faecher-modus.md`
§6).

```markdown
# Personen-Netz – <Familiengruppe / Forschungsfrage>

| Person (mit Jahr/Ort) | Quelle (Kurzzitat) | Datum | Rolle | Ort / Adresse / Hof | Alter, Beruf | unterschreibt / Handzeichen | Bezug zur Zielperson [Status] |
|-----------------------|--------------------|-------|-------|---------------------|--------------|-----------------------------|-------------------------------|
|                       |                    |       | Pate / Zeuge / Anzeigender / Nachbar / Vermieter / Arbeitgeber | | | | |

## Auffälligkeiten
- <Beobachtung> — Hinweis, kein Befund
  Vorhersage: <stimmt die Verbindung → Quelle zeigt X; sonst Y>
  Prüfung: <offen | Protokoll-Verweis, Ergebnis>
```

```markdown
# Person network – <family group / research question>

| Person (with year/place) | Source (short citation) | Date | Role | Place / address / farm | Age, occupation | signs / makes a mark | Relation to target [status] |
|--------------------------|-------------------------|------|------|------------------------|-----------------|----------------------|-----------------------------|
|                          |                         |      | godparent / witness / informant / neighbour / landlord / employer | | | | |

## Observations
- <observation> — a hint, not a finding
  Prediction: <if the link holds → source shows X; otherwise Y>
  Check: <open | log reference, result>
```

## 15. Personen- und Ortsregister / Person and place register

One preferred form per person and place, every variant mapped to it
(`references/ablage-und-erschliessung.md` §5). The same form goes into file
names, tags, notes and replies.

```markdown
# Personenregister – Stand <JJJJ-MM-TT>

| ID | Ansetzungsform | Varianten (mit Quelle) | Kekulé | Externe IDs | Identität [Status] | nicht identisch mit |
|----|----------------|------------------------|--------|-------------|--------------------|---------------------|
| P0001 | NACHNAME, Vorname(n) (*JJJJ Ort) | <Schreibweise — Quelle>; <…> | | MyHeritage: <…> | | P0… |

# Ortsregister – Stand <JJJJ-MM-TT>

| Ansetzungsform | GOV-ID | Historische Namen, Schreibweisen | Pfarrei(en) mit Zeitraum | Standesamt / Verwaltung mit Zeitraum | Verwechslungsgefahr |
|----------------|--------|-----------------------------------|--------------------------|--------------------------------------|---------------------|
|                |        |                                   |                          |                                      |                     |

# Schlagwortliste (zugelassene Begriffe)
quelle: Geburt, Taufe, Heirat, Tod, Begraebnis, Urkunde, Brief, Foto, Militär, Zeitung, Interview, <…>
Verweisungen: <Eheurkunde → Heirat>, <Sterbeurkunde → Tod>, <…>
```

```markdown
# Person register – as of <YYYY-MM-DD>

| ID | Preferred form | Variants (with source) | Kekulé | External IDs | Identity [status] | not identical with |
|----|----------------|------------------------|--------|--------------|-------------------|--------------------|
| P0001 | SURNAME, given name(s) (*YYYY place) | <spelling — source>; <…> | | MyHeritage: <…> | | P0… |

# Place register – as of <YYYY-MM-DD>

| Preferred form | GOV-ID | Historical names, spellings | Parish(es) with period | Register office / administration with period | Easily confused with |
|----------------|--------|-----------------------------|------------------------|----------------------------------------------|----------------------|
|                |        |                             |                        |                                              |                      |

# Tag list (allowed terms)
quelle: Geburt, Taufe, Heirat, Tod, Begraebnis, Urkunde, Brief, Foto, Militär, Zeitung, Interview, <…>
See-references: <Eheurkunde → Heirat>, <Sterbeurkunde → Tod>, <…>
```

## 16. Findbuch Familienunterlagen / Finding aid for family papers

One row per unit, including what relatives hold
(`references/ablage-und-erschliessung.md` §6).

```markdown
# Findbuch Familienunterlagen – Stand <JJJJ-MM-TT>

| Nr. | Einheit (Titel) | Laufzeit | Umfang | Verwahrer, Überlieferungsweg | Zustand | Digitalisiert (ja / teilweise / nein, Ablageort) | Zugang über | Personen (IDs) | Hinweise |
|-----|-----------------|----------|--------|------------------------------|---------|--------------------------------------------------|-------------|----------------|----------|
| F01 | <Fotoalbum, Kasten, Bündel, Familienstammbuch, Bibel> | <JJJJ–JJJJ> | <60 Fotos, 12 Blatt> | <wer, von wem erhalten> | | | <wen fragen> | | |
```

```markdown
# Finding aid for family papers – as of <YYYY-MM-DD>

| No. | Unit (title) | Date range | Extent | Keeper, line of custody | Condition | Digitised (yes / partly / no, location) | Access via | Persons (IDs) | Notes |
|-----|--------------|------------|--------|-------------------------|-----------|------------------------------------------|------------|---------------|-------|
| F01 | <photo album, box, bundle, family register, bible> | <YYYY–YYYY> | <60 photos, 12 leaves> | <who, received from whom> | | | <whom to ask> | | |
```

## 17. Begleitnotiz zu einer Datei / Sidecar note for a file

Lies beside the master under the same base name. The master itself stays
untouched, its metadata included (`references/ablage-und-erschliessung.md`
§7).

```markdown
# Begleitnotiz – <Dateiname des Masters>

Originaldateiname: <wie von Scanner, Gerät oder Portal vergeben>
Prüfsumme (SHA-256): <…>
Zitat: <vollständiges Zitat der Quelle>
Herkunft: <Archiv, Signatur | Verwahrer der Familienunterlage, Findbuch-Nr.>
Fundort und Nachbarschaft: <Album S. 7 zwischen … und …; Bündel; Umschlag>
Seiten: <Vorderseite: Datei · Rückseite: Datei | Rückseite leer>
Datum des Originals: <JJJJ-MM-TT | Schätzung mit Grundlage>
Digitalisiert: <Datum, Gerät, von wem>
Abgebildet / genannt: <ID, Ansetzungsform — sagt wer, wann, wie sicher — [Status]>
Urheber: <Fotograf, Atelier | unbekannt>
Nutzungsbedingungen bei Erhalt: <nur private Forschung | Veröffentlichung mit Genehmigung | frei | unbekannt>
Schlagwörter: <aus der Schlagwortliste>
Bearbeitete Fassungen: <Dateinamen>
```

```markdown
# Sidecar note – <file name of the master>

Original file name: <as assigned by scanner, device or portal>
Checksum (SHA-256): <…>
Citation: <full citation of the source>
Provenance: <repository, call number | keeper of the family papers, finding-aid no.>
Found where, next to what: <album p. 7 between … and …; bundle; envelope>
Sides: <front: file · back: file | back blank>
Date of the original: <YYYY-MM-DD | estimate with its basis>
Digitised: <date, device, by whom>
Pictured / named: <ID, preferred form — says who, when, how sure — [status]>
Creator: <photographer, studio | unknown>
Terms of use at receipt: <private research only | publication with permission | free | unknown>
Tags: <from the tag list>
Derived versions: <file names>
```
