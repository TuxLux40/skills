# Momentum / Flipper firmware GUI architecture

For questions like "make everything vertical like the Momentum main menu" or general app-dev layout questions.

## Screen basics

128×64 monochrome OLED, landscape. That's the physical hardware — it doesn't change; "vertical" always means either a software remap of an unchanged physical screen, or a different arrangement of content within the same landscape frame.

## Two rendering paths — this is the key distinction

**1. Shared widgets** — `submenu`, `variable_item_list`, `dialog_ex`, `text_input`, `byte_input`, `popup`. Reused across most apps' settings/config/list screens. Patch the shared module once, every app using it inherits the change. This is *why* Momentum's vertical menu style could be a single toggle — the main menu is built from exactly this kind of reusable module.

**2. Custom canvas draw callbacks** — the actual functional screens: NFC read view, SubGHz signal graph, IR remote grid, GPIO pin view, Bad USB script progress, games (Snake, Tetris, etc). Each app draws directly to the canvas with hardcoded pixel coordinates (`canvas_draw_str`, `canvas_draw_icon`, `canvas_draw_frame`) tuned for a 128-wide landscape layout. No shared code, no central switch — each app's layout is bespoke.

**Implication**: "make it all vertical" is not a global setting because most of what's interesting about a Flipper app lives in path 2. Getting vertical settings/config screens (path 1) is cheap if Momentum patches the shared modules. Getting vertical NFC/SubGHz/IR/game screens (path 2) means redesigning each app's draw callback individually — genuinely per-app work, not a rewrite of shared infrastructure.

## Momentum's "vertical" main menu is not a physical rotation

It's an alternate **scroll/layout style** for the main-menu widget specifically — one of 9 menu styles Momentum ships — still rendered on the normal 128×64 landscape canvas. It does not use the orientation API described below. Source: `Momentum-Firmware` submodule, main-menu-related module (search for the menu style enum/switch in the GUI application code).

## The real orientation API (different thing, exists but rarely used well)

```c
view_port_set_orientation(view_port, ViewPortOrientationVertical);
```
Physically rotates a viewport 90° — useful for D-pad-on-bottom holding. Options: `Horizontal` (default), `HorizontalFlip`, `Vertical`, `VerticalFlip`.

Important limitation: this rotates the *coordinate frame*, not the *content*. The physical screen is still 128×64 pixels; rotating just remaps which physical pixels correspond to which logical (x,y). An app whose draw callback assumes a 128px-wide logical canvas will get a 64px-wide logical canvas after rotation and will clip or wrap unless its layout is rewritten for the narrower width. A few community FAPs use this deliberately (built specifically for portrait use), but it's opt-in and only looks right if the app's content was designed for it from the start.

## Where to look for real implementation details

`./Momentum-Firmware` submodule in `flipper-stuff` has the actual firmware source. GUI service and shared widgets live under `applications/services/gui/` (canvas, view_port) and `applications/services/gui/modules/` (submenu.c, variable_item_list.c, etc.) in a standard Flipper firmware tree — check that path inside the submodule to confirm current structure since it does shift between firmware versions.
