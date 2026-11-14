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

## Nächste Schritte
1. <Quelle, Archiv, was genau prüfen>
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

## Next steps
1. <source, repository, what exactly to check>
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

**URTEIL / VERDICT:** belegt | wahrscheinlich | möglich | ungeklärt | widerlegt
**Begründung / reasoning:** <…>
**Aktion in MyHeritage:** bestätigen | offen lassen | ablehnen
**Übernehmen / take over:** <Feldliste mit jeweiliger Originalquelle | nichts>
**Nächste Quellen / next sources:** <…>
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

## 8. Sitzungszusammenfassung für die Wissensbasis / Session summary for the KB

```markdown
# Genealogie-Sitzung <JJJJ-MM-TT>
Forschungsfragen: <…>
Geprüfte Quellen: <Zitate; inkl. negativer Ergebnisse mit Suchumfang>
Ergebnisse: <Befund — Status>
Match-Entscheidungen: <Profil — Urteil — Aktion>
Offene Widersprüche: <…>
Verworfen: <Hypothese — Grund>
Nächste Schritte: <priorisiert>
Neue Dateien: <Dateinamen>
```
