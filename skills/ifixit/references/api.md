# iFixit API v2.0 cheat-sheet

Base: `https://www.ifixit.com/api/2.0` — read endpoints need no key. JSON only. Be polite: no bulk crawling, cache results within a session.
Docs: https://www.ifixit.com/api/2.0/doc

| Need | Endpoint | Notes |
|---|---|---|
| Resolve device name | `GET /suggest/{q}?doctypes=device` | Returns canonical `title` + `display_title` + `url`. Do this first. |
| Find guides | `GET /search/{q}?filter=guide&limit=N` | Literal-ish matching. `thinkcentre m715q` → 0 results while `suggest thinkcentre` lists the family. |
| Device page | `GET /wikis/CATEGORY/{title}` | `guides`, `children`, `parts`, `tools`, `repairability_score`, `ancestors`, `solutions_url`. Title with spaces, URL-encoded (the `/Device/Foo_Bar` web URL uses underscores; the API title is the `title` field). |
| Full guide | `GET /guides/{guideid}[?langid=de]` | See fields below. |
| Troubleshooting wiki | `GET /wikis/WIKI/{title}` | For "won't turn on" style pages. |
| Search other types | `GET /search/{q}?filter=device` / `filter=wiki` / `filter=question` | `question` = Answers forum threads. |

## Guide fields that matter

- `difficulty` (Very easy … Very difficult), `time_required` (human string), `time_required_min/max` (seconds)
- `prerequisites[]` — guides that must be done first (e.g. screen removal before battery). **Always surface these.**
- `tools[]`, `parts[]` — `text`, `quantity`, `notes`, `isoptional`, `url` (store link)
- `steps[].lines[]` — `text_raw`, `level` (indent), `bullet`:
  - `icon_caution` → safety warning, keep verbatim
  - `icon_reminder` → reassembly reminder, keep verbatim
  - `icon_note` → tip
  - colours (`black`, `red`, `orange`, …) → match coloured markers in the step photo; meaningless without images, link the guide
- `steps[].media` — images; link the guide URL instead of describing photos you can't see
- `flags` — `GUIDE_STARRED` = staff/featured quality
- `type` — `replacement`, `disassembly`, `teardown`, `technique`, `repair`

## Markup in `text_raw`

`[link|url|label]`, `[guide|id|label]`, `[product|sku|label]`, `''italic''` — the CLI strips these to labels.

## Gotchas

- Guides are per-*exact*-model. `category` on the guide tells you which one; check it matches.
- `langid=de` only returns German if a translation exists; check `available_langids`. Machine translations set `unreviewed_machine_translation`.
- Licence: CC BY-NC-SA 3.0 — cite the guide URL.

## Usage terms (from iFixit's API launch post, still the stated policy)

Source: https://www.ifixit.com/News/3981/the-worlds-first-repair-api (2010, announced v0.1 alpha — that version is obsolete; use 2.0).

- **Non-commercial use is free, no key.** Commercial use or "large, sustained" request volume → request a key at api@ifixit.com. Personal agent lookups are fine; a bulk mirror/crawler is not.
- **Attribution:** link back to the guide.
- **Share-alike:** condensed or edited guide text is a modification → it stays CC BY-NC-SA. Relevant when saving repair notes to a KB or publishing a wiki page: keep the licence + source link on that page.
- The 2010 post says Answers and Parts weren't exposed; in v2.0 they are (`filter=question`, guide `parts[]`).
