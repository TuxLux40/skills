# Sources and Research Tool Guide

## Research Tool Decision Table

Different tools have different capabilities and work on different sites. Pick the right one for the task:

| Tool | Available when | Best for | Known limitations |
|---|---|---|---|
| `tavily_search` | Tavily MCP connected | General web search, finding relevant pages, forum posts | Rate-limited; use `tavily_extract` for specific URLs |
| `tavily_extract` | Tavily MCP connected | Fetching Arch Wiki (bypasses Anubis JS protection), specific pages | Best for single URLs |
| `context7` (`resolve-library-id` + `query-docs`) | Context7 MCP connected | Library/API docs: libusb, python-hidapi, pyusb, openrazer Python API | Library docs only — not hardware forums or device lists |
| `WebFetch` | Always | Static HTML docs, GitHub raw files, linux-usb.org, direct URL fetch | Fails on JS-heavy sites (Arch Wiki online uses Anubis) |
| `WebSearch` | Always | Finding URLs before fetching, scoping a problem area | Returns URLs, not content — follow up with WebFetch/tavily_extract |
| `gh api` | `gh` CLI installed and authenticated | GitHub issues/PRs/commits, source code search via API | Rate-limited without auth token |
| Local arch-wiki-docs | `pacman -S arch-wiki-docs` installed | Offline Arch Wiki (`/usr/share/doc/arch-wiki/html/`) | May lag ~days behind online version |

**Decision logic:**
1. Library/API docs → try Context7 first
2. Specific page URL → try tavily_extract → fall back to WebFetch
3. Finding relevant pages → WebSearch → then fetch top results
4. GitHub issues/source → `gh api` or WebFetch (github.com/org/repo/blob/main/file)
5. If all fail → record gap in `tribal.md` with the source URL for manual follow-up

---

## Per-Source Access Guide

| Source | URL | Best access method | Notes |
|---|---|---|---|
| OpenRGB wiki (GitLab) | gitlab.com/OpenRGBDevelopers/OpenRGB-Wiki/-/blob/stable/home.md | WebFetch (static) | Direct URL fetch works |
| openrgb.org device list | openrgb.org/wiki | WebFetch | Static HTML, no JS |
| openrazer GitHub | github.com/openrazer/openrazer | `gh api` or WebFetch | Issues, device list, source |
| openrazer device constants | github.com/openrazer/openrazer/blob/master/pylib/openrazer/client/constants.py | WebFetch | Raw file |
| philling-dev/rgb-linux-controller | github.com/philling-dev/rgb-linux-controller | WebFetch or `gh api` | Implementation reference |
| Arch Wiki — USB/HID | wiki.archlinux.org/title/USB | tavily_extract URL → or local `arch-wiki-docs` | Anubis blocks plain WebFetch |
| Arch Wiki — udev | wiki.archlinux.org/title/udev | tavily_extract | Same |
| linux-usb.org usbmon | linux-usb.org/usbmon.html | WebFetch | Static HTML |
| python-hidapi docs | trezor.github.io/cython-hidapi | Context7 (`hidapi`) or WebFetch | Context7 preferred for API reference |
| pyusb docs | pyusb.github.io/pyusb | Context7 (`pyusb`) or WebFetch | |
| Wireshark USB docs | wiki.wireshark.org/USB | WebFetch | Static wiki |
| TRCC upstream issue | github.com/Lexonight1/thermalright-trcc-linux/issues/162 | WebFetch | Specific issue |
| Logitech HID++ protocol | github.com/pwr-Solaar/Solaar/blob/master/docs/hidpp-protocol.md | WebFetch | Solaar project docs |

---

## When Searching for New Solutions

When a device or problem isn't covered by the existing reference files:

1. **Check openrgb.org/wiki** — device compatibility database; sorted by manufacturer
2. **Search openrazer issues** — `gh api repos/openrazer/openrazer/issues?q=DEVICE_NAME&state=all`
3. **Search for existing RE work** — `tavily_search "DEVICE_NAME linux usb hid protocol site:github.com"`
4. **Check Arch Linux BBS** — `tavily_search "DEVICE_NAME arch linux"`
5. **Check relevant subreddits** — r/linux_gaming, r/archlinux, r/unixporn (for RGB setups)

After finding a fix:
- If verified: add to the appropriate core reference file (device-ownership, rgb-control, etc.)
- If unverified/anecdotal: add to `tribal.md` with source URL, date, and mechanism
