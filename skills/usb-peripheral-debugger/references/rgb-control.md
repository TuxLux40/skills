# RGB Control — Daemon Arbitration

The core problem: OpenRGB, openrazer, Solaar, Polychromatic, and Piper/ratbagd all want exclusive access to the same `/dev/hidrawN` nodes. Running more than one simultaneously on the same device causes silent failures, reverts, or crashes.

---

## RGB Tool Overview

| Tool | Access method | What it controls | Runs as |
|---|---|---|---|
| **OpenRGB** | libusb (detaches kernel driver) | RGB only, broad device support | GUI / daemon (`openrgb --server`) |
| **openrazer** | DKMS kernel module + daemon | Razer-specific: RGB, DPI, macros, effects | `systemctl --user start openrazer` |
| **Polychromatic** | Frontend for openrazer | Razer devices via openrazer | GUI |
| **Solaar** | HID protocol (hidraw) | Logitech receivers: battery, DPI, macros, some RGB | `systemctl --user start solaar` |
| **Piper / ratbagd** | hidraw via libratbag | Gaming mice: DPI, buttons, some RGB | `ratbagd.service` |

---

## The Onboard Profile Problem

**Symptom:** RGB tool sets colour, but it reverts when the device is reconnected or the tool exits.

**Cause:** The device has an onboard memory (firmware-stored profiles). The tool is writing to the device's live mode (active colour) but not to its firmware profile slot. When the device reconnects, it loads from firmware — which still has the factory default.

**Solutions by device type:**

| Device type | Solution |
|---|---|
| Has onboard profile support in OpenRGB | OpenRGB → Devices → right-click → Save Profile to Device |
| Logitech G-series (onboard profile) | Use LGHUB (Windows) to write firmware profile once; then OpenRGB for live changes on top |
| Razer (openrazer) | Use `razer-cli` or Polychromatic "on login" trigger to re-apply on connect |
| No onboard support at all | Set RGB via autostart on login (`~/.config/autostart/` or systemd user service) |

---

## Single-Controller Strategy

Running two tools on the same device causes conflicts. Pick one based on what you need:

| Device | Need RGB only | Need DPI / profiles / macros too |
|---|---|---|
| Logitech keyboard/mouse | OpenRGB (broader colour control) | Solaar (but limited RGB) or write profile via LGHUB first |
| Razer device | OpenRGB (if supported) | openrazer + Polychromatic |
| Mouse (any) | OpenRGB | Piper + ratbagd (but check OpenRGB device list first) |
| Custom / unknown | RE path → `reverse-engineering.md` | Same |

**To disable a conflicting daemon:**
```bash
# Disable openrazer so OpenRGB gets exclusive access:
systemctl --user disable --now openrazer

# Disable Solaar (re-enable if you need DPI/macro config):
systemctl --user disable --now solaar

# Check what's running:
systemctl --user list-units --type=service --state=running | grep -iE 'razer|logitech|solaar|rgb|piper|rat'
```

---

## OpenRGB Setup

```bash
# Install (Arch):
sudo pacman -S openrgb

# Needed udev rules (included in package, but verify):
ls /etc/udev/rules.d/60-openrgb.rules
# If missing, copy from:
ls /usr/lib/udev/rules.d/60-openrgb.rules

# Reload rules without reboot:
sudo udevadm control --reload-rules && sudo udevadm trigger

# Run server mode (so it persists in background):
openrgb --server --noautoconnect &

# Apply a saved profile:
openrgb --profile "MyProfile.orp"

# Set all devices to a colour (hex, one-shot):
openrgb --color FF0000
```

Common issue — device not detected: check `lsusb` to confirm device is present, then check OpenRGB device compatibility list at openrgb.org/wiki. If device is listed but not detected, check that no other daemon has the hidraw open (`lsof /dev/hidraw*`).

---

## openrazer Setup

```bash
# Install (Arch AUR):
# yay -S openrazer-meta   (includes kernel module + daemon + Python lib)

# Enable DKMS module (auto-rebuilds on kernel update):
sudo dkms install openrazer-driver/$(ls /var/lib/dkms/openrazer-driver/ | tail -1) 2>/dev/null || true

# Check module loaded:
lsmod | grep razer

# Start daemon:
systemctl --user enable --now openrazer

# Check daemon status:
systemctl --user status openrazer

# Common issue — module not loading after kernel update:
dkms status  # check if openrazer is listed for current kernel
# If not: sudo dkms autoinstall
```

Add user to `plugdev` group (required):
```bash
sudo usermod -aG plugdev $USER
```

---

## Polychromatic Setup

Polychromatic is a GUI frontend for openrazer. It does not talk to hardware directly.

```bash
# Install (Arch AUR):
# yay -S polychromatic

# Polychromatic stores device configs here:
ls ~/.config/polychromatic/

# To add support for a new Razer device not yet in openrazer:
# → see reverse-engineering.md for the RE path
# → device class goes in openrazer, Polychromatic auto-discovers via openrazer
```

---

## Solaar Setup

Solaar manages Logitech Unifying and Bolt receivers. It controls DPI, battery, macros, and limited RGB. It conflicts with OpenRGB for hidraw access to the receiver.

```bash
# Install:
sudo pacman -S solaar

# Run (or as user service):
systemctl --user enable --now solaar

# Solaar config lives at:
ls ~/.config/solaar/

# If RGB via OpenRGB is the priority, stop Solaar first:
systemctl --user stop solaar
```

**OpenRGB vs Solaar tradeoff:**
- OpenRGB: better RGB, no DPI/macro management
- Solaar: DPI/battery/macro management, limited RGB (no per-key on most devices)
- Both at once: conflict — hidraw EBUSY, silent write failures

---

## Autostart RGB on Login

When a device has no writable onboard profile, re-apply on login:

```ini
# ~/.config/systemd/user/rgb-apply.service
[Unit]
Description=Apply RGB profile on login
After=graphical-session.target

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 3
ExecStart=openrgb --profile %h/.config/OpenRGB/MyProfile.orp
RemainAfterExit=yes

[Install]
WantedBy=graphical-session.target
```

```bash
systemctl --user enable --now rgb-apply.service
```
