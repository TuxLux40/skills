# Case Study: Razer Leviathan V2 X

Demonstrates: existing audio support (working), RGB support gap (partial), and reverse engineering path to full Polychromatic support.

---

## Device Profile

| Field | Value |
|---|---|
| Model | Razer Leviathan V2 X Soundbar |
| VID | 0x1532 (Razer) |
| PID | Check `lsusb` — find the Razer Leviathan entry |
| Audio | USB audio class (snd-usb-audio) — working |
| RGB | Vendor-specific HID — needs openrazer or RE |

```bash
# Find exact PID:
lsusb | grep -i "razer\|1532"
```

---

## Audio Status: Working

The Leviathan V2 X presents as a standard USB audio class device. The kernel's `snd-usb-audio` driver handles it. PipeWire recognises it and can use it as default sink. No custom daemon needed for audio.

```bash
# Verify audio driver:
udevadm info $(find /dev/snd -name 'pcm*' 2>/dev/null | head -1) 2>/dev/null | grep DRIVER
# Should show snd-usb-audio

# Verify PipeWire sees it:
pactl list sinks | grep -A5 "Leviathan\|1532"
```

Do not install `openrazer` for audio — it adds complexity without benefit for audio.

---

## RGB Status: Partial

Razer's openrazer project has partial Leviathan support. Before starting RE work, check current status:

```bash
# Check if openrazer lists Leviathan as supported:
# (install openrazer-meta first if not installed)
python3 -c "import openrazer.client; d = openrazer.client.DeviceManager(); print([str(x) for x in d.devices])"

# Or check the openrazer device list directly:
# github.com/openrazer/openrazer/blob/master/pylib/openrazer/client/constants.py
```

If openrazer supports it → install and use Polychromatic (see openrazer setup in `rgb-control.md`).

If openrazer does NOT support it → reverse engineering path below.

---

## Reverse Engineering Path (for Polychromatic Support)

**Goal:** Identify the USB HID protocol for Leviathan RGB commands, implement in openrazer, expose via Polychromatic.

### Step 1: Enumerate (RE Phase 1)

```bash
lsusb -d 1532:PPPP -v 2>/dev/null | less
# Look for: bInterfaceClass 3 (HID), wMaxPacketSize, bNumEndpoints
# Usage page 0xFF00+ = vendor-specific = the lighting interface
```

### Step 2: Compare to known Razer protocol

Most Razer devices use a common 90-byte packet structure:
```
Byte 0:  0x00 (report ID)
Byte 1:  0x1F (transaction ID, varies)
Byte 2:  0x00 (remaining packets)
Byte 3:  0x00 (reserved)
Byte 4:  0x00 (reserved)
Byte 5:  data_size
Byte 6:  command_class (e.g., 0x0F for lighting)
Byte 7:  command_id   (e.g., 0x02 for set colour)
Bytes 8+: payload
Byte 89: checksum (XOR of bytes 2-88)
```

Check openrazer source for existing Leviathan-related code:
```bash
# If openrazer is installed:
grep -r "Leviathan\|leviathan\|1532" /usr/lib/python*/site-packages/openrazer/ 2>/dev/null | head -20
# Or search GitHub: github.com/openrazer/openrazer
```

### Step 3: Capture Razer Synapse traffic (Windows VM)

```bash
# Load usbmon:
sudo modprobe usbmon

# Start capture while Razer Synapse sets a colour in the Windows VM:
sudo timeout 30 cat /sys/kernel/debug/usb/usbmon/1u > /tmp/leviathan-capture.txt

# Filter for Razer VID in capture:
grep "1532" /tmp/leviathan-capture.txt | head -40
```

### Step 4: Identify lighting command

Look for `SET_REPORT` control transfers with 90-byte payload. The command class/ID combination for "set static colour" is what you need.

Compare against known openrazer devices — Leviathan likely shares packet format with other Razer headsets or speakers.

### Step 5: Implement in openrazer

1. Add device entry in openrazer's device list (VID:PID + capabilities)
2. Create device driver class inheriting from the closest matching base class
3. Implement `set_static_effect(r, g, b)` using captured command format
4. openrazer daemon hot-reloads; Polychromatic auto-discovers the new device

### Step 6: Test via python-hidapi before openrazer integration

```python
import hid

# Find the lighting interface (vendor-specific usage page):
for dev in hid.enumerate(0x1532, 0x0000):  # 0x0000 = match any PID
    print(dev)

# Open and test a static colour command (adapt packet from captures):
h = hid.device()
h.open(0x1532, YOUR_PID)  # replace YOUR_PID
# Send SET_REPORT with captured lighting command packet
h.write(bytes([0x00, 0x1f, ...]))  # adapt from captures
h.close()
```

---

## openrazer Installation

```bash
# AUR:
yay -S openrazer-meta

# Check module:
dkms status
lsmod | grep razer

# Start daemon:
systemctl --user enable --now openrazer

# Add to plugdev group (required):
sudo usermod -aG plugdev $USER

# After kernel update — rebuild module if dkms didn't auto-rebuild:
sudo dkms autoinstall
```

---

## Polychromatic Setup

Polychromatic is the user interface for openrazer. Once the Leviathan is supported by openrazer, Polychromatic shows it automatically.

```bash
yay -S polychromatic
# Launch via application menu or: polychromatic
```
