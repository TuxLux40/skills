# qFlipper connection troubleshooting (Arch/CachyOS, flatpak qFlipper)

Verified working fix chain, confirmed on oliver's machine 2026-08-02. Root cause has two independent layers — fixing only one leaves qFlipper failing with "Access denied (insufficient permissions)" even though the tty device looks fine.

## Step 0 — find the real device node

Don't assume `/dev/ttyACM0`. Other serial devices (or a stale/leftover node) commonly claim ACM0 first, leaving the actual Flipper on ACM1 or higher.

```bash
journalctl -k --since "10 min ago" | grep -iE "acm|flipper|cdc_acm"
```

Look for a line like:
```
usb 3-1: New USB device found, idVendor=0483, idProduct=5740
usb 3-1: Manufacturer: Flipper Devices Inc.
cdc_acm 3-1:1.0: ttyACM1: USB ACM device
```
That `ttyACM1` (or whatever number appears) is the real target for the rest of this doc. Also note the bus/port path (`3-1` above) — needed later for forcing re-enumeration.

## Step 1 — the udev rule never reaches the host

qFlipper flatpak ships its own udev rule bundled inside the sandbox, but flatpak does **not** install it to the host system:

```bash
find /var/lib/flatpak -iname "42-flipperzero.rules"
# /var/lib/flatpak/app/one.flipperzero.qFlipper/x86_64/stable/<hash>/files/lib/udev/rules.d/42-flipperzero.rules
```

Without this rule on the host, `/dev/ttyACM*` is owned by `root:uucp` with no world/user access, and oliver isn't in the `uucp` group.

## Step 2 — the rule as shipped targets the wrong group

Even after copying it, the rule uses `GROUP="dialout"`:
```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", ATTRS{manufacturer}=="Flipper Devices Inc.", TAG+="uaccess", GROUP="dialout"
```
**Arch/CachyOS has no `dialout` group** — it uses `uucp` for serial devices. `udevadm test` shows `Failed to resolve group 'dialout', ignoring: Unknown group` and the rule's `TAG+="uaccess"` (which is what actually grants the ACL via systemd-logind) silently never applies.

Fix: swap the group before installing.

**This needs a YubiKey touch (sudo) — warn oliver before running:**
```bash
SRC=$(find /var/lib/flatpak/app/one.flipperzero.qFlipper -name 42-flipperzero.rules | head -1)
sudo cp "$SRC" /etc/udev/rules.d/42-flipperzero.rules
sudo sed -i 's/GROUP="dialout"/GROUP="uucp"/' /etc/udev/rules.d/42-flipperzero.rules
sudo udevadm control --reload-rules
```

## Step 3 — force a real re-enumeration

`udevadm trigger` on a device that's already live is frequently a no-op — rules only get re-evaluated on an actual add/remove uevent. Two options:

- **Easiest**: tell oliver to physically unplug/replug the USB cable.
- **Software equivalent** (no physical access needed), toggle the USB `authorized` flag to force the kernel to fully re-enumerate — **needs YubiKey touch**:
```bash
BUSPATH="3-1"   # from Step 0's kernel log line
echo 0 | sudo tee /sys/bus/usb/devices/$BUSPATH/authorized >/dev/null
sleep 1
echo 1 | sudo tee /sys/bus/usb/devices/$BUSPATH/authorized >/dev/null
```

If this only fixes the tty node and the raw USB node (Step 4) still lacks the ACL, retrigger the parent USB device path directly instead of relying on the authorized toggle — **needs YubiKey touch**:
```bash
sudo udevadm trigger --verbose --action=add /sys/bus/usb/devices/$BUSPATH
```

## Step 4 — verify BOTH permission layers

qFlipper needs access to two different device nodes, and they get their ACLs independently:

1. **tty layer** (serial RPC): `/dev/ttyACM1`
2. **raw USB layer** (libusb, used for control transfers / DFU / device registration): `/dev/bus/usb/<bus>/<dev>`

```bash
getfacl /dev/ttyACM1
BUSNUM=$(cat /sys/bus/usb/devices/$BUSPATH/busnum)
DEVNUM=$(cat /sys/bus/usb/devices/$BUSPATH/devnum)
printf -v BUS "%03d" "$BUSNUM"; printf -v DEV "%03d" "$DEVNUM"
getfacl /dev/bus/usb/$BUS/$DEV
```

Both must show a line like `user:oliver:rw-`. If only one has it, the fix only applied to that layer — usually because the retrigger in Step 3 hit the tty child node's uevent but not the parent USB device's own uevent (they're separate events). Re-run the parent-targeted trigger command from Step 3.

Why both are needed: the shipped udev rule uses `SUBSYSTEMS=="usb"` (plural — matches by walking up from whatever device the uevent is actually for) rather than a self-referential `SUBSYSTEM=="usb"` match, so depending on which specific uevent fires, only one of the two related device nodes picks up the tag directly. systemd does propagate `uaccess` tags to some related child nodes automatically, but not reliably across both directions in one trigger — hence checking both explicitly.

## Step 5 — restart qFlipper

Permissions changing while qFlipper is already running doesn't help — it opened (or failed to open) the device once at startup and won't retry cleanly.

```bash
pkill -f 'qFlipper$'
flatpak run one.flipperzero.qFlipper >/tmp/qflipper.log 2>&1 &
sleep 4
tail -30 /tmp/qflipper.log
```

Success looks like:
```
[RPC] RPC session started successfully.
[BKD] Current device changed to "<flipper name>"
```

Failure (permissions still broken) looks like repeated:
```
[USB] Failed to open device: Access denied (insufficient permissions)
```
— if you see this after all steps above, re-check Step 4's ACLs; one of the two layers didn't take.

## Other things to rule out first (quick checks, rarely the actual cause here but cheap to check)

- `ModemManager` grabbing the port: `systemctl is-active ModemManager` (should be inactive/not installed)
- `brltty` (braille display driver, notorious for grabbing random ACM devices): `systemctl is-active brltty`
- Another process already holding the port: `fuser -v /dev/ttyACM1`
