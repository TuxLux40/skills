# Hinweise für spezielle Bestandstypen

Kurzreferenz, wann Standard-Ablageregeln nicht reichen und fachspezifisch anders
vorgegangen werden sollte.

## Bibliotheksgut (Bücher, Publikationen, Sammlungen mit Titeln)

- Formalerschließung orientiert sich an **RDA** (Resource Description and Access)
  bzw. den älteren **RAK**-Regeln: Kernelemente sind Verfasser/Urheber, Titel,
  Erscheinungsjahr, Ausgabebezeichnung. Bei eigenen Sammlungen reicht ein
  vereinfachtes Schema: `Nachname_Vorname--Titel_JJJJ.pdf`.
- **DIN ISO 690** regelt Zitier-/Ansetzungsregeln für Literaturangaben — nützlich als
  Vorbild für konsistente Ansetzung von Personennamen (Nachname zuerst) und
  Titelschreibweise.
- Bestandsaufbau folgt einem **Erwerbungsprofil**: bevor Material aufgenommen wird,
  klären, was thematisch/qualitativ überhaupt reingehört — verhindert unkontrolliertes
  Wachstum irrelevanter Bestände.

## Archivgut (historische/geschäftliche Unterlagen mit Entstehungskontext)

- **Provenienzprinzip** hat Vorrang vor thematischer Neuordnung (siehe
  `aktenplan-und-klassifikation.md`) — der Entstehungszusammenhang ist oft selbst die
  wichtigste Information.
- **Verzeichnung** (Findbuch/Findmittel): pro Akte/Bestand kurze Metadaten erfassen
  (Titel, Laufzeit, Umfang, Herkunft) statt nur den Dateinamen sprechen zu lassen —
  bei großen Beständen lohnt eine separate Übersichtstabelle.
- Vor Aussonderung: **archivische Bewertung**, nicht einfach nach Alter löschen (siehe
  `aufbewahrung-und-kassation.md`).

## Medizinische / personenbezogene Dokumentation

- Höchste Sensibilität: Datenschutz- und Aufbewahrungspflichten sind hier meist
  gesetzlich streng geregelt und **nicht** verhandelbar durch Praktikabilität.
- Zugriffsbeschränkung und Löschfristen sind Teil der Ablagestruktur selbst (z.B.
  getrennte Zugriffsrechte pro Ordner), nicht nur eine Namenskonvention.
- Bei Unsicherheit über Fristen/Zugriffsregeln: nicht raten, auf die einschlägigen
  Vorschriften bzw. eine fachkundige Stelle verweisen.

## Bild-/Mediensammlungen (Bildagentur-Prinzip)

- Metadaten sind hier oft wichtiger als der Dateiname allein: Bildrechte/Lizenz,
  Urheber, Aufnahmedatum, Motiv-Schlagworte — idealerweise eingebettet
  (IPTC/EXIF) statt nur im Dateinamen, weil Bilder oft aus ihrem Ordnerkontext
  herausgelöst weiterverwendet werden.
- Dateiname trotzdem sprechend halten (`JJJJ-MM-TT--Motiv_Kurzbeschreibung.jpg`),
  als Fallback wenn Metadaten verloren gehen (z.B. bei Plattformen, die sie
  strippen).

## Web-/Fremdquellen (heruntergeladene Seiten, PDFs Dritter)

- Herkunft im Namen kennzeichnen (`Web--`-Präfix oder Domain/Autor), damit klar
  bleibt, was zitierfähige Fremdquelle vs. Eigenproduktion ist.
- Begleitende Asset-Ordner (`_files`, `_dateien` bei gespeicherten Webseiten) beim
  Verschieben mitnehmen und synchron umbenennen, sonst brechen relative Verweise
  in der HTML-Datei.
