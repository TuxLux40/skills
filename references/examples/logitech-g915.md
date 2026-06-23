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

**Why OpenRGB can't write the firmware slot:** OpenRGB does not implement G915 onboard profile firmware writing. It controls live colour state only. The onboard profile write requires the full G Hub HID++ protocol, which is not implemented in OpenRGB for the G915.

**Why Solaar can't fix it:** Solaar manages Bolt receiver settings (pairing, DPI, battery status), not G915 per-key RGB profiles.

---

## Working Solutions

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
