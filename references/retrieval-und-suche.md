# Retrieval sicherstellen

Grundlage: Information Retrieval (Boolesche Suche, Indexierung, Thesauri) aus der
FaMI-Ausbildung. Eine Ablage ist nur so gut wie die Wahrscheinlichkeit, eine Datei
später wiederzufinden — Ordnung ohne Retrieval-Denken ist nur Kosmetik.

## Zwei Zugriffswege planen

Jede gute Ablage unterstützt mindestens zwei unabhängige Suchwege, weil man beim
Suchen selten vorhersagen kann, welcher greift:

1. **Navigation** (Browsing) — über die Ordnerstruktur/Klassifikation blättern, wenn
   man weiß, in welchen thematischen Bereich etwas gehört.
2. **Suche** (Retrieval) — Volltext- oder Dateinamensuche, wenn man ein Stichwort,
   einen Namen oder ein Datum kennt, aber nicht mehr, wo es abgelegt wurde.

Konsequenz: Dateinamen und Ordnerstruktur sollten **redundant** genug sein, dass beide
Wege zum Ziel führen — ein guter Dateiname macht die Struktur fehlerverzeihend.

## Boolesche Suchlogik

Klassische Verknüpfung für Suchanfragen (auch relevant, wenn man selbst später mit
`grep`/Spotlight/Dateisuche sucht, oder wenn man Nutzern eine Suche über eine
Sammlung bereitstellt):

- **UND (AND)** — verengt die Trefferzahl, beide Begriffe müssen vorkommen.
- **ODER (OR)** — erweitert, mindestens einer der Begriffe reicht (z.B. Synonyme
  zusammenfassen: `Rechnung OR Faktura`).
- **NICHT (NOT/AND NOT)** — schließt aus, sparsam einsetzen, kann versehentlich
  Treffer verschlucken.

Bei Klassifikationsschemata mit vielen Kategorien hilft dieses Denken beim
Kategorien-Zuschnitt: Eine Kategorie sollte sich klar über UND-Verknüpfungen weniger
Merkmale definieren lassen ("Rechnung UND 2024"), nicht über eine lange Liste von
Ausnahmen.

## Indexierung / Verschlagwortung

Wenn Ordnerstruktur allein nicht reicht (z.B. eine Datei betrifft mehrere Themen
gleichzeitig), zusätzlich verschlagworten statt die Klassifikation zu verbiegen:

- **Tags/Schlagwörter** in Dateisystem-Metadaten, einem Begleit-Index (Tabelle/CSV)
  oder Tools mit Tag-Unterstützung — lösen das Problem, dass eine Datei nur an einem
  Ort im Baum liegen kann, aber mehreren Themen zugehört.
- **Kontrolliertes Vokabular** (Thesaurus-Prinzip): dieselbe Sache immer mit demselben
  Begriff bezeichnen (Deskriptor), Synonyme (Nichtdeskriptoren) auf den Deskriptor
  abbilden. Verhindert, dass "Rechnung", "Faktura" und "Invoice" nebeneinander als
  unterschiedliche Tags existieren und die Suche fragmentieren.
- **Permutiertes Register / KWIC-Prinzip**: bei zusammengesetzten Titeln wird jedes
  bedeutungstragende Wort einmal als Sucheinstieg behandelt (nicht nur das erste
  Wort). Praktische Konsequenz für Dateinamen: das wichtigste Suchwort nicht in der
  Mitte eines langen Namens vergraben, sondern nah an den Anfang stellen.

## Für gepflegte/wachsende Sammlungen

Bei Sammlungen, die über Jahre wachsen (Projektarchive, Firmenablagen), lohnt ein
kurzes **Register/Inhaltsverzeichnis** auf oberster Ebene (README, Findbuch-Prinzip
aus dem Archivwesen: eine separate Übersicht, was in welchem Bestand liegt), damit
man nicht bei jeder Suche den ganzen Baum durchklicken muss.
