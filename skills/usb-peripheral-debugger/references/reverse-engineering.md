# USB HID Reverse Engineering

How to go from "USB device with no Linux support" to working Linux control code. Follows the RE loop: **Enumerate → Capture → Decode → Replicate → Document**. Optionally includes firmware analysis if captures alone are insufficient.

Adapted and iterated from the `hardware-re-usb-hid` skill, with additions for RGB peripheral specifics, rootless Podman USB passthrough, and a broader RE toolchain.

---

## When to Use This

- Device has vendor-specific features (lighting, macros, profile storage, display control) only accessible via proprietary Windows software
- openrazer/OpenRGB device list doesn't include your device
- You want to add a new device to Polychromatic or OpenRGB

**Not for:** non-HID USB (use libusb/pyusb for bulk/CDC/vendor-class); Bluetooth; published protocols (just implement them).

---

## RE Tool Table

| Tool | Role | Install (Arch) |
|---|---|---|
| `lsusb -v` | Full USB descriptor dump | `usbutils` (base) |
| `usbhid-dump` | HID report descriptor extraction | `usbhid-dump` |
| `usbmon` + Wireshark | Live USB packet capture | `usbutils`, `wireshark-qt` |
| `python-hidapi` | Scripted probe / replay via hidraw | `python-hidapi` (AUR) or `pip install hidapi` |
| `pyusb` | Direct libusb access from Python | `python-pyusb` |
| Ghidra | Firmware RE — open source, excellent for ARM | `ghidra` (AUR) |
| Radare2 | Firmware RE — CLI-first, scriptable | `radare2` |
| Cutter | Radare2 GUI frontend | `cutter` (AUR) |
| Rizin | Radare2 fork, actively maintained | `rizin` (AUR) |
| Binary Ninja | Firmware RE — best disassembly UX, commercial | Download from binary.ninja |
| `binwalk` | Firmware unpacking / entropy analysis | `binwalk` (AUR) |
| `rgb-linux-controller` | Implementation reference for RGB commands | github.com/philling-dev/rgb-linux-controller |

---

## Phase 1: Device Reconnaissance

**Goal:** Complete device profile before touching any protocol.

```bash
# Full USB descriptor dump:
lsusb -d VVVV:PPPP -v 2>/dev/null | less
# Replace VVVV:PPPP with your VID:PID (get from `lsusb`)

# USB topology tree:
lsusb -t

# HID report descriptors for each hidraw node:
for h in /sys/class/hidraw/hidraw*/device/report_descriptor; do
  echo "=== $h ==="
  usbhid-dump -d VVVV:PPPP 2>/dev/null || xxd "$h" 2>/dev/null | head -20
done

# Find all hidraw nodes for your device:
for h in /sys/class/hidraw/hidraw*; do
  node=$(basename "$h")
  id=$(cat "$h/device/uevent" 2>/dev/null | grep HID_ID | cut -d= -f2)
  name=$(cat "$h/device/uevent" 2>/dev/null | grep HID_NAME | cut -d= -f2)
  echo "/dev/$node  $id  $name"
done | grep -i "VVVV\|PPPP\|your_device_name"
```

**Document before proceeding:**

| Fact | Source command |
|---|---|
| VID:PID | `lsusb` |
| USB speed | `lsusb -t` (1.5/12/480/5000 Mbps) |
| Interface count & classes | `lsusb -v` — look for `bInterfaceClass 3` (HID) |
| HID report sizes | `wMaxPacketSize` per interface in `lsusb -v` |
| hidraw mapping | loop above |
| Usage pages | report descriptor (`0xFF00+` = vendor-specific) |
| Endpoint types | Interrupt IN/OUT, Bulk, Control |

**Kernel driver unbinding** (needed if hidraw writes fail silently):
```bash
# Check current binding:
ls -la /sys/class/hidraw/hidrawN/device/driver

# Unbind (format from HID_ID in uevent: BBBB:VVVVPPPP.NNNN):
echo -n "0003:046D:C547.0001" | sudo tee /sys/bus/hid/drivers/hid-generic/unbind

# Rebind to restore normal operation:
echo -n "0003:046D:C547.0001" | sudo tee /sys/bus/hid/drivers/hid-generic/bind
```

---

## Phase 2: Protocol Capture

**Goal:** Raw packet captures of device operation, with and without vendor software.

### Passive sniffing (safe — no device interaction)

```bash
# Load usbmon kernel module:
sudo modprobe usbmon

# Find which USB bus your device is on:
lsusb -t   # note the Bus number

# Capture 10 seconds of traffic on bus 1 (adjust number):
sudo timeout 10 cat /sys/kernel/debug/usb/usbmon/1u > /tmp/usb-capture.txt
cat /tmp/usb-capture.txt | head -50
```

### Wireshark USB capture (recommended — better filtering)

```bash
# Give your user capture permissions:
sudo usermod -aG wireshark $USER   # log out and back in

# Or use sudo with wireshark (not ideal):
sudo wireshark &

# In Wireshark: capture on usbmon1 (or usbmonX for your bus)
# Filter: usb.idVendor == 0x046d  (replace with your VID)
# Also useful: usb.transfer_type == 0x01  (Interrupt transfers, common for HID)
```

### Vendor software capture via Windows VM

To see what commands the vendor software sends, run it in a Windows VM with USB passthrough:

**Option A — rootless Podman (dockur/windows):**
```bash
# Requires rootless Podman setup (see examples/logitech-g915.md for Winboat reference)
# USB passthrough in compose: devices: [/dev/bus/usb/...]
# Capture on host: usbmon while vendor software runs inside container
```

**Option B — QEMU/KVM with USB passthrough:**
```bash
# Pass device directly to VM:
qemu-system-x86_64 ... \
  -device usb-host,vendorid=0x046d,productid=0xc547

# Capture on host usbmon while vendor software runs in VM
```

---

## Phase 3: Protocol Decoding

**Goal:** Understand packet structure, command IDs, and what each command does.

**Do not assume a format.** Header structure, field offsets, and status bytes vary per device. Discover from captures.

### Decoding workflow

1. **Framing** — find packet boundaries, report IDs, header structure
2. **Command/response pairs** — map command bytes to observed device behavior
3. **Endianness** — test both little-endian and big-endian for multi-byte fields
4. **Padding** — devices often require exact packet sizes (64, 256, 512 bytes)
5. **State machine** — track required sequences (e.g., "open session before commands")
6. **Error codes** — catalog all non-success responses

### Tools for pattern hunting

```bash
# Search hex dump for patterns:
grep -P "your_pattern" /tmp/usb-capture.txt

# Compare two captures (before and after vendor tool ran):
diff /tmp/capture-before.txt /tmp/capture-after.txt | grep "^[<>]"

# For Razer Leviathan — compare to known openrazer source:
# openrazer uses SET_REPORT with 90-byte packets starting with 0x00 0x1f
# check: github.com/openrazer/openrazer/tree/master/driver
```

### Razer protocol hint

Many Razer devices use a common pattern:
- USB Control Transfer: `SET_REPORT` (type 0x21, request 0x09)
- 90-byte packets: `[0x00, transaction_id, 0x00, 0x00, 0x00, remaining_packets, data_size, command_class, command_id, ...]`
- `GET_REPORT` (type 0xa1, request 0x01) to read response
- Check existing openrazer source in `/usr/share/openrazer/` or GitHub for documented packet formats

---

## Phase 4: Firmware Analysis (Optional)

Use when captures don't fully reveal the protocol, or when you need to understand command dispatch logic.

**Extraction sources (try in order):**
1. Vendor update packages (zip/exe on vendor website — often contains firmware binary)
2. OTA update capture (usbmon during firmware update)
3. Debug interfaces (SWD/JTAG if physically accessible)
4. Flash chip direct read (last resort, hardware needed)

```bash
# Analyse firmware binary:
binwalk firmware.bin
file firmware.bin
strings firmware.bin | grep -iE 'version|build|copyright|arm|cortex|usb|hid'
```

**ARM Cortex-M (common in peripherals):**
- Vector table at offset 0: SP at `[0:4]`, Reset handler at `[4:8]`
- Use Reset handler address to determine flash base address for Ghidra

**In Ghidra:**
1. Import binary → Language: ARM, Thumb mode (common for Cortex-M)
2. Set base address from vector table analysis
3. Search for USB descriptor tables (VID/PID bytes in hex)
4. Find command dispatch: look for switch statements or function pointer tables

**Key targets:**
- USB descriptor tables (VID:PID bytes, string descriptors)
- Command dispatch table (switch/case or function pointer array)
- Display init sequences (SPI/I2C command streams for LCD devices)
- RGB command handlers

---

## Phase 5: Replicate & Validate

**Goal:** Working Python code that controls the device without vendor software.

```python
#!/usr/bin/env python3
import os
import glob
import time
import sys

def find_hidraw(vid, pid, interface_usage=None):
    """Find hidraw node by VID:PID, optionally filtering by HID usage."""
    target_id = f"{vid:04X}:{pid:04X}"
    for h in sorted(glob.glob("/dev/hidraw*")):
        base = os.path.basename(h)
        try:
            uevent = open(f"/sys/class/hidraw/{base}/device/uevent").read()
            # HID_ID format: 0003:046D:C547
            if target_id.upper() in uevent.upper():
                return h
        except:
            pass
    return None

def send_recv(dev_path, packet, size=64):
    """Send a packet and read the response."""
    fd = os.open(dev_path, os.O_RDWR)
    try:
        padded = packet.ljust(size, b'\x00')
        os.write(fd, padded)
        return os.read(fd, size)
    finally:
        os.close(fd)

# Example: probe command IDs (adapt packet format to your device's captures):
def probe_commands(dev_path, report_id=0x00, packet_size=64):
    fd = os.open(dev_path, os.O_RDWR)
    log = open("/tmp/usb-probe-log.txt", "w")
    try:
        for cmd_id in range(0x00, 0x40):
            packet = bytes([report_id, cmd_id]) + b'\x00' * (packet_size - 2)
            try:
                os.write(fd, packet)
                resp = os.read(fd, packet_size)
                line = f"CMD 0x{cmd_id:02X}: {resp[:16].hex()}"
                print(line)
                log.write(line + "\n")
                log.flush()
            except OSError as e:
                line = f"CMD 0x{cmd_id:02X}: ERROR — {e}"
                print(line, file=sys.stderr)
                log.write(line + "\n")
                if e.errno == 19:  # ENODEV — device disconnected
                    print("DEVICE DISCONNECTED — stopping probe")
                    break
            time.sleep(0.05)  # 50ms — prevent overwhelming device
    finally:
        log.close()
        os.close(fd)
```

**Implementation reference:** `github.com/philling-dev/rgb-linux-controller` — study for command format patterns and how to structure a multi-device RGB controller in Python.

### Adding support to Polychromatic

Polychromatic discovers devices via openrazer. To add a new Razer device:
1. Add device support to openrazer (Python class + driver entry)
2. Polychromatic auto-discovers via openrazer's device list
3. If device uses the standard Razer HID protocol, adding it to openrazer is mostly config (VID:PID + supported features)
4. If protocol differs, implement the HID commands in the openrazer driver

Polychromatic device config path: `~/.config/polychromatic/`

---

## Phase 6: Document

Produce these deliverables and save them:

1. **Device profile** — VID:PID, interfaces, hidraw map, packet sizes, endpoint types
2. **Protocol spec** — packet format table, command table, error codes, state machine
3. **Working code** — minimal Python reproducer for each controlled feature
4. **Open questions** — unknowns needing further investigation
5. **Risk assessment** — commands with write/flash/brick potential

Save everything — even failed experiments. The failure log is often as valuable as the success.

---

## Safety Rules

- **Read before write** — always try GET/query commands before SET/write commands
- **Save device state** before modifying anything (dump configs, current profiles)
- **Never flash firmware** without user approval and a known-good backup
- **Watch for bricking signals** — if a command causes USB disconnect (`ENODEV`), **do not retry it**
- **Test one device first** — never batch-apply to multiple devices
- **Log everything** — every packet sent and received, with timestamps
