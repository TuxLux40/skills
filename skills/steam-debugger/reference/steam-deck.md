# Steam Deck — Hardware-Specific Reference

The Steam Deck runs SteamOS (Arch-based) with a locked root FS. Running plain Arch Linux on Deck hardware is supported but loses SteamOS-specific packages.

## Hardware IDs

| Component | LCD (Jupiter) | OLED (Galileo) |
|-----------|--------------|----------------|
| GPU | 1002:163f | 1002:1435 |
| Wi-Fi | 10ec:c822 | 17cb:1103 |
| Bluetooth | 13d3:3553 | 17cb:1103 |

## Firmware shortcuts

| Button combo | Action |
|-------------|--------|
| Volume Up + Power | UEFI settings |
| Volume Down + Power | Boot menu |
| `···` + Power | Valve bootloader menu |
| Volume Down + Power + `···` | Reset UEFI to defaults |
| Volume Up + `···` (plugged in, 10s) | Battery Storage Mode |

## OLED audio setup (on plain Arch)

OLED model needs: firmware files (`sof-vangogh-*`) from `steamdeck-dsp` package (Valve's jupiter repo), kernel 6.1.52+, `alsa-ucm-conf` 1.2.11+. **Easiest:** use Bazzite kernel (`linux-bazzite` or `linux-neptune-65`).

## Wine audio crackling fix (all Deck models)

```bash
# ~/.config/wireplumber/wireplumber.conf.d/51-quantum.conf
monitor.alsa.rules = [{
  matches = [{ node.name = "~alsa_output.*" }]
  actions = { update-props = { clock.min-quantum = 256 } }
}]
```
256 = minimum working value; 512 or 1024 if still crackling. (Full audio reference: `audio.md`)

## Controller

- **Lizard mode** (default without Steam): trackpads = mouse, some buttons = keys
- **sc-controller**: Steam Input alternative for non-Steam use, supports gyro/extra buttons
- **Steam Input**: requires Steam running; creates virtual Xbox controller under `/dev/input`

## Firmware updates

```bash
fwupd   # handles Deck firmware updates
```
LCD firmware F7A0131+ enables `amd_pstate` CPU driver.
