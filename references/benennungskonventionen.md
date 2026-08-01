# Einheitliche Benennungskonventionen

Grundlage: Formalerschließung (RDA, DIN ISO 690 Ansetzungsregeln) — dort geht es
darum, jedes Werk so eindeutig und konsistent zu beschreiben, dass man es später
zweifelsfrei wiederfindet. Dasselbe Prinzip trägt auf Dateinamen.

## Warum das wichtig ist

Ein Dateiname ist der einzige Suchindex, der garantiert überall funktioniert — in
jedem Dateibrowser, jeder Cloud-Sync, jedem `grep`. Eine gute Ablagestruktur bringt
nichts, wenn die Namen darin inkonsistent sind: Retrieval scheitert nicht an der
Struktur, sondern an uneinheitlichen Namen, die weder Sortierung noch Volltextsuche
zuverlässig treffen.

## Element-Reihenfolge

Bewährtes Muster, angelehnt an die Ansetzungslogik der Formalerschließung
(wichtigstes/sortierrelevantes Element zuerst):

```
[Datum]--[Thema/Titel]__[Zusatz].[Endung]
```

- **Datum** in ISO 8601 (`JJJJ-MM-TT`) — sortiert chronologisch und lexikografisch
  gleichzeitig, sprachunabhängig, keine Verwechslung wie bei TT.MM.JJJJ. Nur weglassen,
  wenn kein sinnvolles Bezugsdatum existiert (z.B. bei zeitlosen Referenzwerken).
- **Thema** in `Snake_Case` oder `kebab-case` — konsequent eine der beiden Formen,
  nicht mischen. Leerzeichen in Dateinamen vermeiden (brechen Shell-Befehle, URLs,
  manche Sync-Tools).
- **Zusatz** optional: Version (`_v2`), Bearbeitungsstatus (`_Entwurf`, `_final`),
  Sprache, o.ä. — nur wenn es wirklich zur Unterscheidung nötig ist.

## Regeln, die Retrieval verlässlich machen

- **Ein Name, eine Schreibweise.** Wenn ein Thema mehrfach vorkommt, exakt gleich
  schreiben (nicht einmal "Bibliothek", einmal "Bibliotheken", einmal "Bib").
- **Sonderzeichen minimieren.** Doppelpunkte, Schrägstriche, Fragezeichen sind auf
  manchen Dateisystemen verboten. Anführungszeichen und Gedankenstriche brechen oft
  Skripte/Downloads. Bindestrich `-` und Unterstrich `_` reichen für alle
  Trennfunktionen.
- **Umlaute sind ok**, sofern die Zielumgebung UTF-8-sauber ist (bei Unsicherheit
  transliterieren: ä→ae, ö→oe, ü→ue, ß→ss) — im Zweifel transliterieren, das ist
  robuster über Systemgrenzen hinweg.
- **Keine bedeutungslosen Namen** wie `Dokument1.pdf`, `neu.docx`, `IMG_2384.jpg` ohne
  Kontext — beim Umbenennen den tatsächlichen Inhalt kurz sichten (Titel, Betreff,
  erste Zeile), nicht blind den Original-Dateinamen bereinigen.
- **Kürze vor Vollständigkeit, aber nicht auf Kosten der Eindeutigkeit.** Ein
  Dateiname ist eine Kurzbeschreibung, kein Fließtext — typischerweise 3–8
  aussagekräftige Wörter.

## Herkunft kennzeichnen, wenn relevant

Bei Materialien aus externen Quellen (heruntergeladene Webseiten, fremde Dokumente)
hilft ein Präfix wie `Web--` oder der Verfassername voranzustellen (`Nachname--Titel`,
analog zur Ansetzung von Personennamen in der Katalogisierung) — das macht auf einen
Blick klar, was Eigenproduktion und was Fremdmaterial/Quelle ist.

## Beispiel

Schlecht: `"Grundlagen zum Dokumentenmanagement (2).html"`, `IMG_2384.jpg`,
`Bericht_neu_FINAL_v3_wirklich_final.docx`

Gut: `2024-03-14--Dokumentenmanagement_Grundlagen.html`,
`2024-03-14--Foto_Serverraum.jpg`, `2024-03-14--Jahresbericht_v3.docx`
