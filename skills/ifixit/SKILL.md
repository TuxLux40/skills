---
name: ifixit
description: Hardware repair assistant backed by iFixit's public API (guides, device pages, troubleshooting wikis, tool/part lists). Use whenever the user wants to repair, disassemble, open, upgrade or diagnose physical hardware — phones (Pixel/GrapheneOS), laptops, mini PCs (ThinkCentre Tiny), GPUs, keyboards, controllers, consoles, appliances — or asks "how do I replace X", "teardown", "which screwdriver", "is this repairable", "battery swollen", "thermal paste", "won't power on", or mentions iFixit. Also use for repairability scores and for planning a repair (tools, parts, difficulty, time, risks) before buying anything. Check this skill before improvising disassembly steps from memory.
---

# iFixit hardware repair

Goal: get the user from "broken thing" to a **safe, concrete, sourced repair plan** — never invented disassembly steps. iFixit guides are community-maintained and photographed; your memory of screw counts and clip locations is not. Fetch, then summarize.

## Workflow

1. **Identify the exact device.** Model number beats marketing name (`M715q` ≠ `M75q Gen 2`; Pixel 8 ≠ 8 Pro — different batteries, different guides). Ask for the label/type number if ambiguous.
2. **Resolve it on iFixit** — `scripts/ifixit.py suggest "<name>"` returns canonical device titles. Search is literal; a near-miss name returns 0 results, not a fuzzy match.
3. **Pull the device page** — `scripts/ifixit.py device "<Title>"` lists guides, troubleshooting, child models, repairability score.
4. **Pick the guide** — `scripts/ifixit.py search "<device> <part>"` if not on the device page. Prefer `GUIDE_STARRED` / iFixit-authored, then most recent `modified_date`.
5. **Fetch it** — `scripts/ifixit.py guide <id>` renders steps as Markdown with caution/warning bullets preserved. Pass `--lang de` for German if available.
6. **Plan before touching anything** — output the checklist below. Read `references/safety.md` when batteries, mains power, capacitors, adhesive or glass are involved (they usually are).
7. **No guide found?** Walk the fallback ladder in `references/fallbacks.md` (sibling model, chassis family, Answers forum, manufacturer HMM/service manual). Say explicitly that the guide is for a *different* model and which steps are likely to differ.

Container/proxy blocks `www.ifixit.com`? Use a web-fetch/scrape tool on the same API URLs (`references/api.md`) — the JSON is identical.

## Repair plan output (always this shape)

```
Device:      <exact model> — iFixit: <device URL>
Guide:       <title> (<difficulty>, ~<time>) — <guide URL>
Risk flags:  <battery / adhesive / ribbon cables / mains / ESD / warranty / water seal>
Tools:       <from guide `tools`, mark optional ones>
Parts:       <from guide `parts`; part number if known>
Prereqs:     <prerequisite guides that must be done first>
Steps:       <condensed; keep every caution/warning line verbatim>
Point of no return: <first step that is destructive or breaks a seal>
Reassembly:  <reverse-order caveats, torque/adhesive/re-seal notes>
```

Mark the **point of no return** explicitly — the step where adhesive/glass/water-sealing is broken. Everything before it is reversible; that's where the user decides go/no-go.

## Hard rules

- **Never fabricate** screw sizes, counts, connector locations or clip positions. If the guide doesn't say, say "guide doesn't specify".
- **Keep warning lines verbatim** (`bullet: icon_caution` / `icon_reminder` / `icon_note`). Condense the rest.
- **Lithium batteries:** discharge to <25 %, never puncture/bend, swollen = stop and dispose properly (DE: Wertstoffhof / Händler-Rücknahme, not household waste). See `references/safety.md`.
- **Mains & PSUs / CRTs / microwaves:** capacitors hold lethal charge after unplugging. Do not walk a user through internal mains work without flagging this first.
- **GrapheneOS Pixel:** a screen or USB-C board swap is fine; board/fingerprint replacements may need re-pairing via Google's repair tool — mention it, and that the verified-boot key is unaffected by hardware swaps.
- Attribute iFixit content (CC BY-NC-SA) with the guide URL — don't paste whole guides as your own. Condensed guides saved to a KB/wiki stay CC BY-NC-SA (share-alike); keep the source link there. Heavy/commercial API use needs a key — see `references/api.md`.

## Helpers

| File | Use |
|---|---|
| `scripts/ifixit.py` | stdlib-only CLI: `suggest`, `search`, `device`, `guide`, `--json` for raw output |
| `references/api.md` | endpoint cheat-sheet, field meanings, gotchas |
| `references/safety.md` | battery, capacitor, ESD, adhesive/heat, glass, disposal (DE) |
| `references/fallbacks.md` | what to do when iFixit has no guide for the exact model |
| `references/hardware-inventory.template.md` | template for a **private** device inventory (keep the filled copy out of public repos) |

## Logging

After a repair, offer to log it to the KB: device, guide URL, what actually differed from the guide, parts source + price, outcome. Those deltas are the valuable part — they're what the next repair needs.
