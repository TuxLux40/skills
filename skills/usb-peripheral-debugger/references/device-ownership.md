# Device Ownership

How to find out exactly who controls a USB peripheral at any layer of the stack.

---

## Finding Who Owns a Device

### Quick ownership check

```bash
# Who has any hidraw open right now?
lsof /dev/hidraw* 2>/dev/null

# Which PIDs have input event devices open?
fuser -v /dev/input/event* 2>/dev/null

# Combined: show all processes touching USB/HID devices
lsof /dev/hidraw* /dev/input/event* /dev/bus/usb/*/* 2>/dev/null | awk 'NR==1 || /hidraw|input|bus/'
```

### Kernel's view of a device

```bash
# Get VID:PID, driver, subsystem for hidraw node N:
udevadm info /dev/hidrawN

# Follow the full device chain up to the root hub:
udevadm info --tree /dev/hidrawN

# Show all properties including DEVPATH, HID_ID, HID_NAME:
udevadm info --query=all /dev/hidrawN
```

`HID_ID` format: `0003:0000046D:0000C547` → bus 3 (USB), VID `046d`, PID `c547`

### Mapping VID:PID to hidraw nodes

A single USB device can have multiple HID interfaces (and thus multiple hidraw nodes). Example with a Logitech receiver:

```bash
# List all hidraw nodes and their HID_NAME / HID_UNIQ
for h in /sys/class/hidraw/hidraw*; do
  node=$(basename "$h")
  name=$(cat "$h/device/uevent" 2>/dev/null | grep HID_NAME | cut -d= -f2)
  id=$(cat "$h/device/uevent" 2>/dev/null | grep HID_ID | cut -d= -f2)
  echo "/dev/$node  $id  $name"
done
```

### Live kernel events (watch device connect/disconnect/bind)

```bash
udevadm monitor --environment --udev
# Filter for HID/USB:
udevadm monitor --environment --udev 2>/dev/null | grep -E 'SUBSYSTEM|DEVNAME|ACTION|HID_NAME'
```

### Kernel messages about USB/HID

```bash
# Last 50 USB-related kernel messages:
dmesg | grep -iE 'usb|hid' | tail -50

# Watch live:
dmesg -w | grep -iE 'usb|hid'

# Journalctl equivalent (includes timestamp):
journalctl -k --since "1 hour ago" | grep -iE 'usb|hid'
```

---

## Understanding HID Interface Numbering

A single physical device creates one hidraw node per HID interface. Example:

| Device | HID interfaces | hidraw nodes |
|---|---|---|
| Simple keyboard | 1 (keyboard HID) | 1 |
| Logitech G915 via Bolt | 4 (keyboard, media, G-keys, receiver mgmt) | 4 |
| Razer headset | 2 (audio HID, lighting/macro HID) | 2 |
| Thermalright TRCC LCD | 1 (vendor HID) | 1 |

Run `lsusb -v -d VID:PID` and look for `bInterfaceClass 3` (HID) entries — each is a separate hidraw node.

---

## Detaching the Kernel Driver (for Direct Access)

Some tools (OpenRGB, pyusb) need to claim an interface directly via libusb, which requires detaching the kernel HID driver first:

```bash
# Find the device's kernel binding:
ls -la /sys/class/hidraw/hidrawN/device/driver

# Unbind (use the HID_ID value from udevadm — format: BBBB:VVVVPPPP):
echo -n "0003:046D:C547.0001" | sudo tee /sys/bus/hid/drivers/hid-generic/unbind

# OpenRGB / libusb handle this automatically via libusb_detach_kernel_driver()
# If writes fail silently, driver is still attached — detach manually
```

To rebind after (restore normal operation):
```bash
echo -n "0003:046D:C547.0001" | sudo tee /sys/bus/hid/drivers/hid-generic/bind
```

---

## udev Rules for Permissions

Most RGB tools need read/write on the device. Common udev rule pattern:

```
# /etc/udev/rules.d/99-usb-peripherals.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="046d", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1532", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1532", MODE="0660", GROUP="plugdev"
```

Reload without reboot:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Check your user is in `plugdev`:
```bash
groups $USER | grep plugdev
# Add if missing:
sudo usermod -aG plugdev $USER  # log out and back in for it to take effect
```
