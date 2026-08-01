---
name: windows-styling-guide
description: >
  Translate Windows 11 Fluent Design Language into KDE Plasma theming constructs.
  Use this skill whenever the user wants to make KDE look like Windows 11, recreate
  the Fluent Design aesthetic in Plasma, replicate Windows UI elements (Mica/Acrylic
  translucency, rounded corners, elevation shadows, accent colors, Segoe typography),
  or asks about "Windows-style KDE theme", "Windows 11 theme for KDE", "Fluent theme",
  "make KDE look like Windows", "mica effect in KDE", or any Windows visual design
  concept in a KDE context. Always invoke alongside the kde-theming skill — this
  skill provides the design token mapping; kde-theming provides the implementation
  mechanics.
---

# Windows 11 Fluent Design → KDE Theming Guide

This skill maps the official Windows 11 design language (sourced from Microsoft's
desktop app guidelines, updated March 2026) to concrete KDE Plasma theming values.
Use in conjunction with the **kde-theming** skill, which covers SVG element IDs,
Aurorae structure, and KWin effects API.

---

## Design Principles to Keep in Mind

Windows 11 prioritizes these qualities — match them when designing the KDE theme:

| Win11 Principle | What it means for your KDE theme |
|---|---|
| **Effortless** | Clean, uncluttered panels. Minimal decoration. |
| **Calm** | Neutral base palette. Subtle shadows. Color used sparingly. |
| **Personal** | Follow system accent color. Support light/dark switching. |
| **Familiar** | Keep standard KDE interaction patterns — don't surprise the user. |
| **Complete** | Consistent corner radii, shadows, and spacing everywhere. |

---

## Color System

### Light / Dark Modes

Windows 11 uses two modes. Map them to KDE color schemes:

| Win11 concept | KDE equivalent |
|---|---|
| Light mode | A color scheme with `[Colors:Window] BackgroundNormal=#FFFFFF` and dark text |
| Dark mode | A color scheme with `[Colors:Window] BackgroundNormal=#202020` and light text |
| Default follow-system | Ship two `.colors` files; user selects in System Settings |

**Key principle:** Darker backgrounds = less important. Lighter surfaces = higher visual priority. In KDE Plasma Style SVGs, the panel/widget background should be the mid-tone; dialogs/popups should float above with a lighter (light mode) or slightly lighter-dark (dark mode) fill.

### Accent Color

- Win11 default accent: **#0078D4** (Windows Blue)
- Accent is used **sparingly** — only on active/focused/selected states
- In the KDE `colors` file, set `[Colors:Selection] BackgroundNormal=#0078D4`
- Buttons, toggles, progress bars, checked states use accent
- Avoid accent on backgrounds or decorative elements

### Recommended Palette (light mode baseline)

```
App background (Mica base):    #F3F3F3  (warm off-white)
Card / elevated surface:       #FFFFFF
Panel / sidebar:               #F9F9F9
Stroke / border:               rgba(0,0,0,0.08)  → approx #EBEBEB
Primary text:                  #1A1A1A
Secondary text:                #616161
Disabled text:                 #A0A0A0
Accent:                        #0078D4
Accent hover:                  #006CBE
Accent pressed:                #005FAD
```

Dark mode equivalents:
```
App background (Mica base):    #202020
Card / elevated surface:       #2C2C2C
Panel / sidebar:               #272727
Stroke / border:               rgba(255,255,255,0.08)
Primary text:                  #FFFFFF
Secondary text:                #ABABAB
Accent:                        #60CDFF  (Win11 dark-mode accent blue)
```

---

## Elevation & Shadows

Win11 uses elevation values + stroke-width to communicate layering. Shadow intensity varies by theme.

| Surface | Elevation value | Stroke width | KDE mapping |
|---|---|---|---|
| Window | 128 | 1 | Aurorae decoration shadow |
| Dialog | 128 | 1 | `dialogs/background.svg` shadow glow |
| Flyout / Menu | 32 | 1 | `widgets/tooltip.svg`, popup background |
| Tooltip | 16 | 1 | `widgets/tooltip.svg` |
| Card | 8 | 1 | Contained widget backgrounds |
| Control (rest/hover) | 2 | 1 | Button/input borders |
| Control (pressed) | 1 | 1 | Pressed state — shadow collapses |
| Flat layer | 1 | 1 | Base layer, no visual shadow |

**Rule:** Higher elevation → larger, softer shadow. Lower elevation → tight or no shadow.

### Translating to Aurorae / Plasma SVG

For **window shadows** (Aurorae):
- Use KWin shadow blur. Recommended for Win11 feel: `ShadowOffset=32`, blur spread `~64px`
- Shadow color: `rgba(0,0,0,0.15)` light mode / `rgba(0,0,0,0.35)` dark mode
- In `<ThemeName>rc`: `ShadowColor=0,0,0` with low opacity

For **flyout/dialog shadows** in Plasma Style SVGs:
- Add a soft drop-shadow filter to the SVG `background` element
- Use a `<filter>` with `feDropShadow` — stdDeviation around 8–16px, dy=4, opacity=0.12

**Layering system** — Win11 uses two explicit layers:
1. **Base layer** — navigation, commands, menus (slightly off-white / slightly lighter dark)
2. **Content layer** — main content area (pure white / slightly elevated dark)

Map this to Plasma Style by giving the panel a slightly tinted background vs widget content areas a purer white/dark.

---

## Geometry (Corner Radii)

Win11 is consistent about this. Apply these radii everywhere in SVGs and QML:

| Context | Corner radius | Win11 examples → KDE target |
|---|---|---|
| Top-level overlays | **8px** | Windows, dialogs, flyouts, menus → Aurorae decoration, `dialogs/background.svg`, `widgets/tooltip.svg` |
| In-page controls | **4px** | Buttons, inputs, checkboxes, lists → button SVGs, input borders |
| Bar elements | **4px** | Progress bars, sliders, scrollbars |
| Touching elements | **0px** | Split buttons, attached flyouts → no rounding on shared edge |
| Maximized / snapped | **0px** | Windows docked to edges |

In Aurorae's `<ThemeName>rc`:
```ini
[General]
# No direct corner radius setting — bake it into decoration.svg
# The 8px rounded frame goes in the SVG corner elements
```

In `decoration.svg`, draw the `decoration-topleft` / `decoration-topright` corners with an 8px arc. The `decoration-bottomleft` / `decoration-bottomright` corners also 8px when not maximized.

For Plasma Style widget SVGs, round the `center` element's path to 8px for dialog backgrounds, 4px for panel-background.

---

## Materials: Mica & Acrylic in KDE

Win11 uses two named materials:

### Mica
- Samples the desktop wallpaper color — blends app with the environment
- Used for the **main app window background** (not transient surfaces)
- Distinguishes focused vs unfocused windows
- **KDE equivalent:** Enable KWin's blur effect + a semi-transparent Plasma Style background
  - In `plasmarc`: `[Wallpaper] BlurRadius=64`
  - Set `background-color: rgba(255,255,255,0.7)` in the Plasma Style SVG (light mode)
  - Dark: `rgba(32,32,32,0.8)`
  - Aurorae decoration: set `Blur=1` in `<ThemeName>rc`

### Acrylic
- Blurs content **behind** a transient surface (flyout, menu, notification)
- More transparent/blurry than Mica
- **KDE equivalent:** `widgets/tooltip.svg` and `dialogs/background.svg` with KWin blur
  - Lower opacity: `rgba(255,255,255,0.6)` light / `rgba(28,28,28,0.75)` dark
  - Requires KWin blur effect enabled (`kcmshell6 kwincompositing`)
  - In `plasmarc` add: `[ContrastEffect] enabled=true\nintensity=0.65\ncontrast=0.45\nsat=1.7`

---

## Typography

Win11 uses **Segoe UI Variable** exclusively. For KDE:

| Win11 role | Font / size | KDE color scheme key |
|---|---|---|
| Display (large titles) | Segoe UI Variable / 68pt | — |
| Title Large | Segoe UI Variable / 40pt | — |
| Title | Segoe UI Variable / 28pt | `[WM] ActiveFont` |
| Subtitle | Segoe UI Variable SemiBold / 20pt | — |
| Body (default) | Segoe UI Variable / 14pt | System font setting |
| Body Strong | Segoe UI Variable SemiBold / 14pt | — |
| Caption | Segoe UI Variable / 12pt | — |

**Practical advice for KDE:**
- Set the system font to **Segoe UI** (if installed) or **Inter** / **Noto Sans** as a fallback
- Font weight for labels: Regular (400); bold labels use SemiBold (600)
- Never use anything below 12pt in a Windows-style theme

---

## Iconography

| Win11 system | KDE equivalent |
|---|---|
| **Segoe Fluent Icons** (system glyphs) | Plasma system icons — use a Windows-style icon theme |
| Single-line style (1epx stroke, minimal) | Look for icon themes like `Win11-icon-theme` or `Fluent` on KDE Store |
| App icons: simple, single-metaphor | Use `.ico` → PNG converted at 16/22/32/48/256px sizes |
| Icon sizes: 16, 20, 24, 32, 48 | KDE standard sizes: 16, 22, 32, 48, 64, 128 |

For a Windows-feel icon set:
- Install **Fluent** or **Windows-11** icon theme from the KDE Store
- Set in System Settings → Appearance → Icons

---

## Putting It Together: KDE Component Mapping

| Windows 11 element | KDE theming target | Notes |
|---|---|---|
| Window frame + titlebar | Aurorae decoration | 8px corners in SVG, Win11-style close/min/max button shapes |
| Close button (red ×) | `close.svg` in Aurorae | Win11 uses a subtle ×, red only on hover |
| Window shadow | Aurorae `ShadowOffset`/blur | Soft, large spread (~64px), low opacity |
| Panel | `widgets/panel-background.svg` | Acrylic-style semi-transparent |
| Taskbar | Panel + plasmoid styling | Centered taskbar, rounded buttons |
| Start menu / launcher | Kickoff / Application Launcher | Hard to make pixel-perfect; use community plasmoids |
| Context menus | `widgets/tooltip.svg` or menu | 8px corners, acrylic, 32-elevation shadow |
| Tooltips | `widgets/tooltip.svg` | 4px corners, 16-elevation shadow |
| Dialogs | `dialogs/background.svg` | 8px corners, 128-elevation shadow, modal scrim |
| Scrollbar | `widgets/scrollbar.svg` | Thin (6–8px) when at rest, wider on hover |
| Notification | `widgets/tooltip.svg` variant | Match flyout style |

---

## Quick Recipe: Minimal Win11 KDE Theme

1. **Fork Breeze** as base: `cp -r /usr/share/plasma/desktoptheme/default ~/.local/share/plasma/desktoptheme/win11-fluent`
2. **Set colors** in the `colors` file: accent `#0078D4`, backgrounds as above
3. **Round SVG corners** in `panel-background.svg` and `dialogs/background.svg` to 8px
4. **Enable blur** in `plasmarc` for panel and dialogs
5. **Create Aurorae decoration** with 8px frame corners, soft shadow, thin buttons
6. **Set font** to Segoe UI Variable or Inter
7. **Install Fluent icon theme** from KDE Store
8. **Enable KWin blur + translucency** effects in compositor settings

See the **kde-theming** skill for exact SVG element IDs, `metadata.json` format, and cache-clearing commands.

---

## Common Pitfalls

- **Don't over-blur** — Mica is subtle. Heavy blur looks more macOS than Windows.
- **Don't over-round** — Win11 uses 8px max on frames. Very large radii (16px+) look wrong.
- **Accent sparingly** — only interactive/active states. Win11 does NOT use accent as a panel background color.
- **Shadows need contrast** — On dark mode, increase shadow opacity (0.35+) or shadows vanish.
- **Stroke matters** — All Win11 surfaces have a 1px border. Add a subtle `rgba(0,0,0,0.08)` stroke to SVG backgrounds in light mode.
- **KWin blur requires compositing** — if disabled, fallback to a solid semi-transparent color.
