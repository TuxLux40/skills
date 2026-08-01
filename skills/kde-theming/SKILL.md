---
name: kde-theming
description: >
  Create, scaffold, and explain KDE Plasma theming. Covers all four pillars of
  KDE visual customization: Plasma Styles (SVG desktop themes — panel, widgets,
  clock), Aurorae window decorations (KWin titlebar/button SVGs), Plasma
  widgets/plasmoids (QML), and KWin declarative effects. Use this skill whenever
  the user mentions: making a KDE theme, customizing Plasma appearance, creating
  a window decoration, writing a plasmoid, KWin effects, "how do I theme X in
  KDE", "make a Plasma style", or any variation of "KDE theming." Also trigger
  for questions about SVG element IDs in Plasma, the colors file format, metadata.json
  for KDE packages, or debugging why a Plasma style isn't loading.
---

# KDE Theming

## Quick orientation

Ask yourself (or the user) which area applies:

| What they want to theme | Type |
|---|---|
| Panel, desktop, tooltips, widgets, clock face | **Plasma Style** |
| Window titlebar + close/min/max buttons | **Aurorae decoration** |
| A new widget/applet on the desktop | **Plasma Widget (QML)** |
| Visual compositor effect (slide, fade, etc.) | **KWin Effect** |
| Wallpaper accent color | **Wallpaper metadata** |

If the user doesn't specify, ask one clarifying question. If they say "a theme", they almost certainly mean Plasma Style.

---

## Plasma Styles

Read `references/plasma-style.md` for the full reference. Core workflow below.

### Install location
```
~/.local/share/plasma/desktoptheme/<theme-id>/
```
System themes live in `/usr/share/plasma/desktoptheme/`. Always work in the user location.

### Scaffold a new theme

The fastest start is forking Breeze:
```bash
cp -r /usr/share/plasma/desktoptheme/default ~/.local/share/plasma/desktoptheme/mytheme
```
Then edit `metadata.json` — the `Id` must match the folder name.

To scaffold from scratch, generate these minimum files:
```
mytheme/
├── metadata.json          # required
├── colors                 # optional but strongly recommended
├── plasmarc               # optional (blur/contrast/fallback)
├── widgets/
│   └── panel-background.svg
└── dialogs/
    └── background.svg
```

See `references/plasma-style.md` → "SVG structure" for element ID requirements in each SVG.

### metadata.json (Plasma 6 / KDE Frameworks 6+)
```json
{
    "KPlugin": {
        "Authors": [{"Name": "You", "Email": "you@example.com"}],
        "Name": "My Theme",
        "Description": "A short description",
        "Id": "mytheme",
        "Version": "0.1",
        "License": "GPL"
    },
    "X-Plasma-API": "5.0"
}
```
Bump `Version` every time you change SVGs so Plasma refreshes its cache.

### Testing & cache clearing
```bash
rm -r ~/.cache/plasma*
plasmashell --replace &
```
Or select the theme in **System Settings → Appearance → Plasma Style**.

### Color scheme integration

To make SVGs follow system colors, add a `hint-apply-color-scheme` element anywhere in the SVG. For fine-grained control, embed a `<style id="current-color-scheme">` block and use `ColorScheme-Text`, `ColorScheme-Highlight`, etc. as CSS classes with `fill="currentColor"`.

---

## Aurorae Window Decorations

Read `references/aurorae.md` for layout config reference. Core workflow:

### Install location
```
~/.local/share/aurorae/themes/<ThemeName>/
```

### Package structure
```
MyDecoration/
├── metadata.desktop
├── MyDecorationrc        # must be <FolderName>rc
├── decoration.svg        # window frame (9-slice: topleft/top/topright/…/center)
├── close.svg
├── maximize.svg
├── minimize.svg
└── restore.svg           # optional
```

### metadata.desktop
```ini
[Desktop Entry]
Name=My Decoration
Comment=A custom window decoration
X-KDE-PluginInfo-Name=MyDecoration
X-KDE-PluginInfo-Author=You
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=GPL
```

### decoration.svg element IDs

The window frame uses a 9-slice FrameSvg. Required elements (prefix = `decoration`):
- `decoration-topleft`, `decoration-top`, `decoration-topright`
- `decoration-left`, `decoration-center`, `decoration-right`
- `decoration-bottomleft`, `decoration-bottom`, `decoration-bottomright`

Additional prefixes: `decoration-inactive` (dimmed windows), `decoration-maximized` (maximized state).

### Button SVGs

Each button SVG needs at minimum an `active` element (the center). Optional states: `inactive`, `hover`, `hover-inactive`, `pressed`, `deactivated`.

Supported buttons: `close`, `minimize`, `maximize`, `restore`, `alldesktops`, `keepabove`, `keepbelow`, `shade`, `help`.

---

## Plasma Widgets (Plasmoids)

Read `references/widgets.md` for QML API reference.

### Install location
```
~/.local/share/plasma/plasmoids/<com.yourname.widgetid>/
```
Use reverse-DNS naming, e.g. `com.github.yourname.myClock`.

### Scaffold from an existing widget (recommended)
```bash
cp -r /usr/share/plasma/plasmoids/org.kde.plasma.analogclock \
       ~/.local/share/plasma/plasmoids/com.yourname.mywidget
# Edit Id and Name in metadata.json, remove Name[xx] translation lines
```

### Minimum structure
```
com.yourname.mywidget/
├── metadata.json
└── contents/
    └── ui/
        └── main.qml
```

### metadata.json
```json
{
    "KPlugin": {
        "Id": "com.yourname.mywidget",
        "Name": "My Widget",
        "Description": "Does something cool",
        "Authors": [{"Name": "You", "Email": "you@example.com"}],
        "Category": "Utilities",
        "License": "GPL",
        "Version": "1.0"
    },
    "X-Plasma-API-Minimum-Version": "6.0",
    "KPackageStructure": "Plasma/Applet"
}
```

### Testing
```bash
plasmawindowed com.yourname.mywidget
```

---

## KWin Declarative Effects

Read `references/kwin-effects.md` for the QML API.

### Structure
```
my-effect/
└── package/
    ├── metadata.json
    └── contents/
        └── ui/
            └── main.qml   # entry point
```

### metadata.json
```json
{
    "KPackageStructure": "KWin/Effect",
    "KPlugin": {
        "Authors": [{"Email": "you@example.com", "Name": "You"}],
        "Category": "Appearance",
        "Description": "My effect",
        "EnabledByDefault": false,
        "Id": "my-effect",
        "License": "MIT",
        "Name": "My Effect"
    },
    "X-KDE-Ordering": 60,
    "X-Plasma-API": "declarativescript"
}
```

### Install
```bash
kpackagetool6 --type KWin/Effect --install package/
```

---

## Wallpaper Accent Colors

In the wallpaper's `metadata.json`, add:
```json
{
    "KPlugin": {"Id": "mywallpaper", "Name": "My Wallpaper", "License": "CC-BY-SA-4.0"},
    "X-KDE-PlasmaImageWallpaper-AccentColor": "#3daee9"
}
```
Use `{"Light": "#color", "Dark": "#color"}` for light/dark-aware variants.

---

## Common Gotchas

- **Plasma Style SVGs not updating?** Clear `~/.cache/plasma*` and restart plasmashell. Also bump `Version` in `metadata.json`.
- **Element IDs must be exact.** Wrong IDs silently fall back to Breeze. Check IDs in Inkscape via Object → Object Properties.
- **Prior to KF6:** themes used `metadata.desktop` instead of `metadata.json`, and `plasmarc` was merged into `metadata.desktop`. Stick with `metadata.json` for new themes.
- **`hint-apply-color-scheme`** makes Plasma colorize the SVG; omit it if you want pixel-perfect custom colors.
- **Border tiling vs stretching:** borders are tiled by default; add a `hint-stretch-borders` element if you want them stretched.
- **Center element:** scaled by default; add `hint-tile-center` to tile instead.
- **Aurorae:** if a button SVG is missing entirely, that button won't appear — there's no Breeze fallback for buttons.
