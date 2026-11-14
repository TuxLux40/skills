# Schnittstellen-Katalog / Data access catalogue

Which sources offer an official machine interface or export, and what the
result is worth as evidence. This file is knowledge only — no client code
lives in this skill (planned for a separate MCP repository). Interfaces
change: confirm on the provider's developer page before building on one.
Entries marked *(verify)* were not cross-checked when this file was written.

## 1. Order of access

1. **Export by the user** from their own account (GEDCOM, DNA match and
   segment lists).
2. **Official API** of the provider.
3. **Open archive standards**: IIIF (images + manifests), OAI-PMH and SRU
   (metadata harvesting and search), SPARQL endpoints.
4. **Fetching freely reachable pages**, including systematically across a
   holding. Pace requests, identify the client honestly, cache what was
   fetched, keep the fetched page with URL and timestamp as the source copy.

Access-restricted portals (login, paywall, captcha, technical blocks) are not
covered here; how to work with them is decided together with the MCP code.
Until then the user retrieves from those portals and hands over images or
exports.

Whatever the route: a 403/429/503, a login wall or an empty result page is
logged as **"nicht geprüft"**, never as "nicht gefunden".

## 2. Catalogue

| Source | Interface | Account / key | Delivers | Evidence value |
|--------|-----------|---------------|----------|----------------|
| **MyHeritage** (tree) | GEDCOM export: Family tree → Manage trees → Export to GEDCOM; the export contains links to photos | own account | The whole tree incl. citations | The user's own compilation; input for `gedcom_plausi.py` |
| **MyHeritage** (DNA) | Download of the DNA match list and of shared segments as files *(verify current menu path and availability per plan)* | own account | Matches, shared cM, segments | Raw data for the segment table |
| **MyHeritage** developer API | Existence and terms of a public API *(verify — not confirmed)* | — | — | — |
| **GOV** (CompGen gazetteer) | REST/JSON by GOV-ID (Swagger UI at gov.genealogy.net/swagger-ui) and SOAP services incl. search by name | none for reading | Place identity, parish and administrative affiliation over time | Compiled reference; cite GOV-ID |
| **CompGen databases** (GEDBAS, Online-OFB, Verlustlisten, Adressbücher, Grabsteine, Familienanzeigen) | Web search; **Metasuche** (meta.genealogy.net) across them; no documented API *(verify)* | none | Index hits, OFB family sheets | Derivative / compilation → lead |
| **Deutsche Digitale Bibliothek / Archivportal-D** | Public API (api.deutsche-digitale-bibliothek.de, v1 and v2; OpenAPI description) | parts need a key *(verify which)* | Finding-aid metadata, digitised objects, newspapers | Finding aid; the linked digitised item may be an original image |
| **Landesarchiv NRW** (archive.nrw.de) | Web finding aids with stable links to units and images | none | Civil-register and church-book duplicates | Image of original / official duplicate |
| **Matricula** | Web viewer with stable image URLs; no documented API *(verify)* | none | Church-book images | Image of original |
| **Archion**, **Ancestry** | No public API | subscription | — | See section 1 |
| **FamilySearch** | Developer API (OAuth 2; app key works against beta at once, **production access needs a compatibility review**) | account + approved app | Tree, search, places; record images are subject to per-collection restrictions | Index = derivative; image = as the original |
| **Open Archieven** (NL/BE) | Public JSON API (api.openarch.nl) | none | Indexed records with link to the holding archive | Index → fetch the scan |
| **WikiTree** | Public API (api.wikitree.com) | none for public profiles | Collaborative tree profiles | Compilation → lead |
| **Geni** | API with OAuth *(verify)* | account | Tree profiles | Compilation → lead |
| **Wikidata** | SPARQL endpoint | none | Place histories, notable persons | Compiled; follow the references |
| **Internet Archive** | Search and full-text APIs | none | Digitised books, address books, periodicals | Depends on the item; cite the scan page |
| **Chronicling America** (Library of Congress) | Public API (loc.gov) | none | US newspapers, OCR | OCR is a finding aid; read the page image |
| **Gallica** (BnF) | SRU search, IIIF images, OCR | none | French books, newspapers | As above |
| **US National Archives Catalog** | API v2 (catalog.archives.gov/api/v2) | free API key (`x-api-key`) | Catalogue descriptions, digitised items where available | Finding aid; item scans as the original |
| **Arolsen Archives** | Online archive (collections.arolsen-archives.org) with search; enquiries by form; no documented public API *(verify)* | none | Persecution, forced labour, DP documents | Image of original |
| **Europeana** | Public API *(verify)* | key | Aggregated cultural-heritage metadata | Finding aid |
| **Transkribus** | API for handwritten-text recognition (public models incl. Kurrent) | account, usage-based | Machine transcription | Provisional reading — same status as any machine reading |
| **DNA Painter** | Import of segment data into a chromosome map (map settings → "Import segment data") | account | Visual segment map | Presentation of the user's own table |

## 3. Rules for anything fetched by machine

- Store the raw response or page copy unaltered beside the extracted data,
  with URL, access time and query.
- An API record is an **index entry**. Evidence is the image or original it
  points to; fetch that and cite it.
- Name variants: run each query with the variants from
  `regionale-besonderheiten.md`; log which variants were run.
- Do not write to any external tree or database from a script. Changes to
  the master tree are made by the user.
- Keep credentials out of notes, logs and the repository.
