---
name: flipper-zero
description: Manage oliver's Flipper Zero device and his flipper-stuff repo (~/Projects/flipper-stuff, github.com/TuxLux40/flipper-stuff) on CachyOS/Arch. Use this whenever oliver mentions Flipper Zero, qFlipper, flipper-stuff, Momentum firmware, or asks to push/deploy/sync files (BadUSB payloads, SubGHz captures, IR remotes, NFC/RFID dumps, dolphin animations, JS scripts) to a Flipper. Also use for qFlipper "device busy" / "access denied" / can't-connect problems, for questions about where a given resource pack comes from, and for Flipper app/firmware GUI development questions (canvas layout, vertical vs horizontal orientation, submenu/widget architecture). Trigger even if oliver just says "flipper" without more detail — check this skill before improvising.
---

# Flipper Zero (oliver's setup)

Host facts: CachyOS/Arch, qFlipper installed as a **flatpak** (`one.flipperzero.qFlipper`), sudo requires a **YubiKey touch** (pam_u2f) — always tell oliver a command needs a touch before running it, `sudo -n` fails silently otherwise.

Repo: `~/Projects/flipper-stuff` — a submodule aggregator, not itself firmware or an app. Two deploy scripts live at its root, `install_to_flipper.py` and `copy_to_sd.sh`. There is no `.gitmodules`-tracked README; treat this SKILL.md as the map.

## Connection problems ("device busy", "access denied", qFlipper won't see the Flipper)

Read `references/connection-troubleshooting.md` before improvising — it's a fully-verified fix chain (confirmed working 2026-08-02), not a guess. Short version: the flatpak never installs its udev rule to the host, and the rule as shipped uses a group (`dialout`) that doesn't exist on Arch. Both the tty device (`/dev/ttyACM*`) and the raw USB node (`/dev/bus/usb/<bus>/<dev>`) need fixing independently — qFlipper needs both.

Don't assume the Flipper is on `/dev/ttyACM0`. Check `journalctl -k` for the actual `cdc_acm` assignment; it's commonly `ttyACM1` on this machine because other serial devices grab ACM0 first.

## Deploying files to the Flipper

Two scripts, pick by size/patience:

- **`install_to_flipper.py`** — pushes over USB serial using Momentum's `flipper.storage` Python module. Convenient (no disassembly), but slow — the SubGHz and Wav Player datasets (627MB–2.4GB) are deliberately commented out of its `TRANSFERS` list for this reason. Update `PORT` in the script if the device isn't on `/dev/ttyACM0` (see above).
- **`copy_to_sd.sh`** — pulls the microSD card and rsyncs directly via a card reader. Much faster for bulk data, includes the large SubGHz/Wav dirs the USB script skips. Auto-detects the card by `LABEL=FLIPPER` or by looking for `badusb`/`infrared`/`subghz` folders on a mounted volume; pass a mountpoint explicitly if autodetect fails.

Default to the USB script for small/incremental pushes (new BadUSB payload, a few IR files); default to the SD script for a fresh card or bulk resync.

Before either: check `~/Projects/flipper-stuff/SD Card Resources/<category>/README.md` — some categories have manually-curated notes that aren't just submodule mirrors.

## Resource map (what's a submodule, what it contains)

| Submodule | Source | Content |
|---|---|---|
| `Flipper` | UberGuidoZ | The big one — `Dolphin_Level`, `Infrared`, `BadUSB`, `NFC`, `RFID`, `Music_Player`, `Sub-GHz`, `Wav_Player` |
| `BadUSB-Files-For-FlipperZero` | beigeworm | BadUSB payload pack |
| `badusb` | FalsePhilosopher | BadUSB payload pack (second source) |
| `Flipper-IRDB` | UberGuidoZ | IR remote database (~94MB) |
| `FlipperZero-Subghz-DB` | Zero-Sploit | SubGHz capture database |
| `Flipper-Zero-Demodulation-Scripts` | gulickO2 | SubGHz demodulation scripts |
| `flipper-zero-js-scripts` | MrPotatoXx | JS scripting examples |
| `Momentum-Firmware` | Next-Flip | Firmware source itself — check here for exact GUI module code |
| `awesome-flipperzero` | djsime1 | Curated link list, not files |
| `FroggMaster` | FroggMaster | Upstream notes/docs (mirrored into `Notes and Documentation/`) |

Update everything: `git submodule update --remote --merge` from repo root.

## Momentum / firmware GUI dev questions

Read `references/momentum-gui-architecture.md` for the canvas/orientation/widget-vs-custom-draw breakdown — covers why "make everything vertical like the Momentum main menu" isn't a one-line fix, and where in `Momentum-Firmware` to look for the real implementation.
