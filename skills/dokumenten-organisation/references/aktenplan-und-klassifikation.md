# Aktenplan und Klassifikation

Grundlage: Archivwissenschaft (Provenienzprinzip, Aktenplan) und Bestandsaufbau-Lehre
aus der FaMI-Ausbildung.

## Zwei Ordnungsprinzipien

1. **Provenienzprinzip** (Herkunftsprinzip) — Unterlagen bleiben in der Struktur, in
   der sie entstanden sind (z.B. nach Projekt, Absender, Abteilung). Bewahrt Kontext
   und Entstehungszusammenhang. Standard im Archivwesen.
2. **Pertinenzprinzip** (Betreffsprinzip) — Unterlagen werden nach Sachthema neu
   geordnet, unabhängig von Herkunft. Praktischer für schnellen thematischen Zugriff,
   zerstört aber den Entstehungskontext.

Für private/geschäftliche Dateiablage meist eine **Mischform** sinnvoll: oberste Ebene
nach Pertinenz (Sachthema/Lebensbereich), darunter chronologisch oder nach Projekt.

## Aufbau eines Aktenplans

Ein Aktenplan (Klassifikationsschema) sollte:

- **Hierarchisch, aber flach** sein — max. 3–4 Ebenen, sonst wird Navigation mühsam.
- **Trennscharf** sein — jede Datei hat genau einen eindeutigen Ort. Wenn eine Datei
  in zwei Kategorien passen könnte, ist die Kategorie zu grob geschnitten.
- **Stabil, aber erweiterbar** sein — neue Themen sollten sich anfügen lassen, ohne
  bestehende Struktur umzubauen. Nummerierte Präfixe (01_, 02_, ...) halten die
  Sortierung stabil, auch wenn später Kategorien dazwischen eingefügt werden (Lücken
  lassen: 01, 02, 05, 10 ... statt 01, 02, 03).
- **Aus dem Bestand abgeleitet**, nicht aus einer Wunschvorstellung. Erst inventarisieren
  (siehe `scripts/inventory.py`), dann Kategorien aus den tatsächlich vorhandenen
  Themen bilden — keine leeren Schubladen für hypothetische Zukunft anlegen.

## Vorgehen bei einer Neuordnung

1. **Inventur** — alle Dateien auflisten, grob nach Thema/Typ clustern lassen.
2. **Kategorien ableiten** — wiederkehrende Themen als Kategorien vorschlagen, jede
   mit 1-Satz-Begründung. Grenzfälle (Datei passt in mehrere Kategorien) explizit
   benennen und eine Entscheidung treffen statt sie offenzulassen.
3. **Mit Nutzer abstimmen** — bei größeren Beständen (>~30 Dateien) die vorgeschlagene
   Struktur vor dem eigentlichen Verschieben kurz zeigen. Verschieben ist über `git mv`
   oder normales `mv` leicht reversibel, wenn's im Repo passiert — trotzdem lohnt der
   kurze Check, weil falsche Kategorien später mühsam zu entwirren sind.
4. **Ausführen** — verschieben/umbenennen in einem Rutsch, nicht schrittweise über viele
   einzelne Edit-Aktionen.
5. **Dokumentieren** — kurze Übersicht (README oder Kommentar), was wo liegt und warum,
   besonders wenn die Struktur nicht selbsterklärend ist.

## Bestandsgruppenprofile

Bei größeren, wachsenden Sammlungen (Bibliotheks-/Archivbestand, aber auch ein
Firmen-Fileserver) lohnt sich ein kurzes **Profil pro Kategorie**: Was gehört rein,
was bewusst nicht, wer legt ab, wie lange wird's aufbewahrt (siehe
`aufbewahrung-und-kassation.md`). Das verhindert, dass die Struktur über Zeit
"vermüllt", weil jeder eigene Interpretationen der Kategorien nutzt.
