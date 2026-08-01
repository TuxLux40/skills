---
name: dokumenten-organisation
description: Ordnet, benennt und erschließt Dateien und Dokumente einheitlich, damit sie später wiederauffindbar sind — angewandte Methodik aus Archiv-, Bibliotheks- und Dokumentationswissenschaft (Aktenplan/Klassifikation, RDA/DIN-ISO-690-Benennungslogik, Boolesche Retrieval-Prinzipien, Aufbewahrung/Kassation). Immer nutzen, wenn der Nutzer eine chaotische Dateiablage, einen vollen Downloads-Ordner oder eine unstrukturierte Dokumentensammlung aufräumen, sortieren, kategorisieren, einheitlich umbenennen oder in ein Dokumentenmanagement-System (DMS) überführen will — auch wenn er nicht explizit "Katalogisieren" oder "Erschließen" sagt. Ebenso nutzen bei Fragen zu Dateinamens-Konventionen, Ordnerstrukturen, Aktenplänen, Aufbewahrungsfristen, Verschlagwortung/Tagging oder wie man eine Sammlung später leichter wiederfindet.
---

# Dokumenten-Organisation

Diese Skill überträgt die Methodik professioneller Informationserschließung
(Archivwesen, Bibliothekswesen, Dokumentationswissenschaft) auf ganz praktische
Aufräum-Aufgaben: einen vollen Ordner, eine Sammlung von PDFs, einen Fileserver,
eine Downloads-Ablage. Die Fachdisziplinen haben über Jahrzehnte gelöst, wie man
große Mengen heterogener Dokumente so ordnet, dass man sie zuverlässig wiederfindet
— dieselben Prinzipien tragen eins zu eins auf "meine Dateien sind ein Chaos".

## Warum das mehr ist als "Dateien in Ordner schieben"

Reines Aufräumen nach Bauchgefühl erzeugt oft eine Struktur, die beim Anlegen
einleuchtet, aber sechs Monate später nicht mehr — weil Kategorien uneindeutig
waren, Namen inkonsistent sind oder es keinen zweiten Zugriffsweg neben der
Ordnerstruktur gibt. Die vier Referenzdateien in `references/` behandeln genau
diese Fallstricke, jeweils mit der Begründung *warum* eine Regel wichtig ist —
nicht nur *was* zu tun ist.

## Vorgehen

### 1. Inventur

Nie blind drauflos sortieren. Erst den tatsächlichen Bestand erfassen:

```bash
python3 scripts/inventory.py <verzeichnis>
```

Das Skript listet alle Dateien rein lesend nach Typ, Größe, Änderungsdatum — macht
keine Änderungen. Bei sehr großen Beständen `--json` für maschinenlesbare Ausgabe
nutzen. Für einen schnellen Überblick reicht bei kleineren Ordnern auch `ls`/`find`
direkt.

Aus der Inventur ergeben sich meist schon die natürlichen Themen-Cluster — nicht
raten, welche Kategorien "sinnvoll klingen", sondern aus den tatsächlich
vorkommenden Themen ableiten. Details zum Kategorien-Zuschnitt:
**`references/aktenplan-und-klassifikation.md`**.

### 2. Struktur vorschlagen und abstimmen

Bei überschaubaren Beständen (grob < 30 Dateien) direkt eine Struktur vorschlagen
und umsetzen. Bei größeren oder für den Nutzer bedeutsamen Beständen (persönliche
Dokumente, geschäftliche Unterlagen, alte Sammlungen mit unklarem Wert) die
vorgeschlagene Ordnerstruktur kurz zeigen, bevor draufgeschrieben/verschoben wird —
falsch zugeschnittene Kategorien sind später mühsamer zu entwirren als sie vorher
kurz abzustimmen.

Faustregel für den Zuschnitt: jede Kategorie trennscharf, hierarchisch aber flach
(max. 3–4 Ebenen), nummerierte Präfixe für stabile Sortierung. Details:
**`references/aktenplan-und-klassifikation.md`**.

### 3. Einheitlich benennen

Konsistente Dateinamen sind der wichtigste Hebel für spätere Auffindbarkeit — noch
vor der Ordnerstruktur, weil Namen überall funktionieren (Suche, Sync, Sortierung),
Ordnerstrukturen nicht immer. Kernmuster: `JJJJ-MM-TT--Thema_in_Snake_Case.endung`.
Details zu Element-Reihenfolge, Sonderzeichen, Umlauten, Herkunftskennzeichnung:
**`references/benennungskonventionen.md`**.

### 4. Auffindbarkeit gegenprüfen

Bevor eine Struktur als fertig gilt, kurz durchdenken: Findet man eine beliebige
Datei sowohl über Durchklicken der Ordner als auch über Namens-/Volltextsuche
wieder? Braucht es zusätzlich Tags/ein Register, weil manche Dateien in mehrere
Kategorien passen? Details zu Booleschen Suchprinzipien, Verschlagwortung,
Registern: **`references/retrieval-und-suche.md`**.

### 5. Aussondern statt nur anhäufen

Wenn beim Aufräumen offensichtlich veraltete Duplikate oder wertlose Zwischenstände
auftauchen: nicht automatisch löschen, sondern bewertend vorgehen und bei fremden
oder unklaren Beständen die Löschentscheidung dem Nutzer überlassen. Details:
**`references/aufbewahrung-und-kassation.md`**.

### 6. Spezialfälle

Bibliotheksgut, Archivgut, medizinische/personenbezogene Unterlagen und
Bild-/Mediensammlungen folgen jeweils eigenen fachlichen Konventionen (RDA,
Provenienzprinzip, Datenschutzfristen, IPTC-Metadaten). Kurzreferenz mit Verweis,
wann Standardregeln nicht reichen: **`references/spezialbestaende.md`**.

## Ausführung

- Verschieben/Umbenennen in einem programmatischen Durchgang erledigen (Skript oder
  Batch von `mv`-Befehlen), nicht Datei für Datei über einzelne Edit-Aktionen — bei
  hunderten Dateien ist das der einzige praktikable Weg und reduziert Fehlerquellen
  durch Wiederholung.
- Zusammengehörige Dateien (z.B. eine `.html`-Datei mit ihrem `_files`-Assets-Ordner)
  gemeinsam verschieben und synchron umbenennen.
- Nach dem Verschieben kurz verifizieren: nichts verloren gegangen, keine Datei
  doppelt gelandet, Zielordner enthalten was sie sollen.
- Bei Unsicherheit über Löschungen: verschieben statt löschen, siehe
  `references/aufbewahrung-und-kassation.md`.
