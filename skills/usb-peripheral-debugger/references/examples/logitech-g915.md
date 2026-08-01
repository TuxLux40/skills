# Case Study: Logitech G915 TKL Wireless

Demonstrates the onboard-profile problem, daemon conflict detection, and workarounds for OpenRGB limitations on Bolt receiver devices.

---

## Device Profile

| Field | Value |
|---|---|
| Model | Logitech G915 TKL Wireless (Lightspeed) |
| USB receiver | Logitech Bolt (046d:c548) |
| Keyboard VID:PID | 046d:c547 (on receiver) |
| HID interfaces | ~4 (keyboard, media keys, G-keys, receiver mgmt) |
| hidraw nodes | 4 nodes — one per interface |

---

## Problem: Rainbow Revert

**Symptom:** OpenRGB sets per-key RGB, looks correct immediately, then resets to rainbow animation after disconnect or power-cycle.

**Root cause:** Onboard memory slot 0 was never written. The G915 has 3 onboard profile slots stored in its firmware. Slot 0 is the factory default (rainbow animation). OpenRGB writes to the device's "live mode" (active colour state) but does not write the onboard firmware slot. On reconnect, the device loads slot 0 from firmware → rainbow.

**Why OpenRGB can't write the firmware slot:** OpenRGB does not implement G915 onboard profile firmware writing. It controls live colour state only.

**Solaar CAN write the onboard flash (CONFIRMED 2026-06-26).** Earlier notes here said it couldn't — wrong, and it cost a multi-hour session. Solaar's `logitech_receiver.hidpp20.OnboardProfiles` reads AND writes the onboard profiles with correct CRCs. See "Persisting onboard profiles from Linux" below. Hand-rolling the HID++ writes is the trap — it almost works and silently fails.

---

## Persisting onboard profiles from Linux (the real fix)

⚠️ **Community** — uses Solaar's internal API. This writes the keyboard's firmware flash, so colours survive power-cycle/reboot with **no daemon running**.

```python
import sys; sys.path.insert(0, "/usr/lib/python3.14/site-packages")
from logitech_receiver import base, receiver
from logitech_receiver.hidpp20 import OnboardProfiles, LEDEffectSetting
from logitech_receiver.hidpp20_constants import SupportedFeature

# G915 is device [1] on the Lightspeed receiver (/dev/hidraw9), NOT direct hidraw14.
# Solaar MUST be stopped first — exclusive hidraw access.
dev = None
for di in base.receivers_and_devices():
    if getattr(di, "isDevice", False):
        continue
    r = receiver.create_receiver(base, di)
    for n in range(1, 7):
        cd = r[n] if r else None
        if cd and "G915" in (cd.name or "").upper():
            dev = cd; break
    if dev: break

dev.ping()
prof = OnboardProfiles.from_device(dev)          # reads real profiles + sizes
static = lambda R,G,B: LEDEffectSetting.from_bytes(bytes([0x01,R,G,B,0,0,0,0,0,0,0]))
for idx, rgb in {1:(0xFF,0xFF,0xFF), 2:(0x00,0xBC,0xFF)}.items():
    p = prof.profiles[idx]
    p.lighting[0] = static(*rgb); p.lighting[1] = static(*rgb)  # zone 0=primary, 1=logo
prof.write(dev)                                  # writes control sector 0 + each profile, with CRC16
dev.feature_request(SupportedFeature.ONBOARD_PROFILES, 0x30, 0, 1)   # activate profile 1
```

**Why hand-rolled HID++ writes fail** (all three matter): sector size is **255**, not 254; every sector ends with a **crc16** (`common.crc16`, CCITT poly 0x1021) — writing `0x0000` makes firmware reject the profile and revert to rainbow; the **control/directory sector 0** must be written too (`prof.write` does it first). Also `ReadSector` (fn 0x50) returns the write *buffer*, not committed flash — so bad writes read back as "correct" while the keyboard stays invalid.

**Mode trap:** Solaar `rgb_control: 1` (software mode) paints ONE global colour over every profile — looks like a persistent solid colour but it's Solaar repainting on each connect, not the flash, and it kills per-profile switching. Set `rgb_control: 0` (onboard mode) to let the flash drive per-profile colours. `brightness_control` must be > 0 or LEDs stay dark.

---

## Working Solutions (live-mode fallback, if flash write isn't an option)

### Option A: Re-apply on login via systemd autostart

Instead of persisting the profile in firmware, re-apply it every time the desktop session starts. Works well when the device is always connected to the same machine.

```ini
# ~/.config/systemd/user/g915-rgb.service
[Unit]
Description=Apply G915 RGB profile on login
After=graphical-session.target

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 5
ExecStart=openrgb --profile %h/.config/OpenRGB/G915.orp
RemainAfterExit=yes

[Install]
WantedBy=graphical-session.target
```

```bash
systemctl --user enable --now g915-rgb.service
```

Adjust the sleep duration if the device needs more time to enumerate after login.

### Option B: Use OpenRGB server + udev trigger

OpenRGB in server mode can re-apply a profile when the device reconnects via a udev rule:

```bash
# /etc/udev/rules.d/99-g915-rgb.rules
ACTION=="add", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c548", \
    RUN+="/usr/bin/openrgb --profile /home/USER/.config/OpenRGB/G915.orp"
```

Reload udev rules: `sudo udevadm control --reload-rules`

### Option C: Check current openrgb.org for onboard support status

OpenRGB device support changes with releases. Check the device compatibility page before assuming onboard write is impossible:
- openrgb.org/wiki (device list) — look for G915 entry and "Save to Device" support column

---

## Bolt Receiver hidraw Conflict

```
G915 via Bolt receiver (046d:c548)
├── /dev/hidraw0  ← OpenRGB targets this (keyboard interface, per-key RGB)
├── /dev/hidraw1  ← Solaar targets this  (receiver management, pairing, battery)
├── /dev/hidraw2  ← kernel input (G-keys — safe to share)
└── /dev/hidraw3  ← kernel input (media keys — safe to share)
```

OpenRGB and Solaar target **different** hidraw nodes, so they can coexist. Verify there is no actual conflict:

```bash
lsof /dev/hidraw* 2>/dev/null
# Each node should have at most one opener
```

If both try to claim the same node (can happen depending on Bolt firmware version), one must be disabled. Prefer whichever provides the features you need more — RGB (OpenRGB) or DPI/battery monitoring (Solaar).

---

## Detecting the Live Mode Limitation

To verify the profile is in live mode vs firmware:

1. Set a colour with OpenRGB
2. Disconnect the keyboard from USB (or turn it off)
3. Reconnect
4. If it reverts to rainbow → live mode only, firmware slot 0 is default

To check if your openrgb version supports onboard save:
```bash
openrgb --version
# Then check openrgb.org/wiki for G915 support in that version
```
