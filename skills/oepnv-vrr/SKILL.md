---
name: oepnv-vrr
description: "Hilft bei ÖPNV-Verbindungen im Verkehrsverbund Rhein-Ruhr (VRR/NRW). Nutze bei Fahrplanfragen, Routenplanung, Linienvergleichen, Gleisen, Umstiegen und typischen Fallen (falsche Linie einsteigen)."
type: workflow
lifecycle: active
---

# ÖPNV VRR — Verbindungen & Fallen vermeiden

Praktische Unterstützung für Verbindungen im Verkehrsverbund Rhein-Ruhr (VRR). Immer aktuelle Apps für Echtzeitdaten prüfen.

## Workflow

1. **Ziel und Zeit klären**: Ankunftszeit, Startbahnhof, Zielbahnhof.
2. **Linien prüfen**: Direkte Regionalexpress-Linien bevorzugen, wenn vorhanden. Auf Zielanzeige und Liniennummer achten.
3. **Kombinationen bauen**: Direktverbindung vs. S-Bahn + Umstieg.
4. **Gleis + Live-Info**: Typische Gleisbelegungen als Orientierung, dann immer DB Navigator / VRR-App für aktuelle Verspätungen und Gleiswechsel.
5. **Fallen vermeiden**: Siehe `references/fallen.md`.

## Wichtige Linien (Beispiele Ruhrgebiet ↔ Düsseldorf/Neuss)

| Linie | Typische Route | Hinweise |
|-------|----------------|----------|
| **RE6** (RRX) | Minden – Bielefeld – Hamm – Dortmund – Essen – Duisburg – Düsseldorf – Neuss – Köln | Hält in Neuss Hbf. Gute Direktverbindung Ruhr → Neuss/Köln. |
| **RE5** (RRX) | Wesel – Oberhausen – Duisburg – Düsseldorf – Köln | Hält **nicht** in Neuss Hbf. |
| **S6** | Essen – Ratingen – Düsseldorf Hbf – (weiter Richtung Köln) | Gute S-Bahn-Verbindung Ruhr → Düsseldorf. |
| **S8** | Hagen – Wuppertal – Düsseldorf – Neuss – Büttgen – Mönchengladbach | Für Ziele wie Büttgen oder Mönchengladbach. |
| **S11** | D-Flughafen – Düsseldorf – Neuss – Dormagen – Köln | Alternative über Neuss Richtung Köln. |

## Typische Hinweise (Werktag)

- RE6 Essen Hbf → Neuss Hbf: ca. 50–55 min, Abfahrten oft zur Minute :32.
- Gleis Essen Hbf (RE6 Richtung Köln): oft 2.
- Gleis Neuss Hbf (RE6 Richtung Köln): oft 3 oder 4.
- S6 Essen Hbf: oft Gleis 12; Düsseldorf Hbf oft Gleis 14.

**Immer in der App gegenprüfen** – Gleise und Zeiten können sich ändern.

## Ressourcen

Siehe `references/ressourcen.md` für Apps, Webseiten und Linienpläne.

## Fallen

Siehe `references/fallen.md` für typische Fehler (falsche Linie, Gleis, etc.).

## Ausgabeformat für Verbindungen

Immer Tabelle mit Spalten:
- Kombination
- Abfahrt Start
- Route
- Ankunft Ziel
- Gleis (Start / Ziel)
- Dauer / Umstieg
- Aktuelle Info (Hinweis: in App prüfen)
