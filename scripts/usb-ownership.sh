#!/bin/sh
# usb-ownership.sh — who currently holds each USB/HID device
# Read-only. Degrades gracefully if tools are missing.
LC_ALL=C

have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n=== %s ===\n' "$1"; }

section "USB Topology"
if have lsusb; then
    lsusb -t 2>/dev/null
else
    echo "(skipped: lsusb not found — install usbutils)"
fi

section "USB Devices (VID:PID + description)"
if have lsusb; then
    lsusb 2>/dev/null
else
    echo "(skipped)"
fi

section "hidraw Nodes and Their Devices"
if [ -d /sys/class/hidraw ]; then
    for h in /sys/class/hidraw/hidraw*; do
        node=$(basename "$h")
        id=$(cat "$h/device/uevent" 2>/dev/null | grep HID_ID | cut -d= -f2)
        name=$(cat "$h/device/uevent" 2>/dev/null | grep HID_NAME | cut -d= -f2)
        driver=$(readlink "$h/device/driver" 2>/dev/null | xargs basename 2>/dev/null || echo "(no driver)")
        printf "  /dev/%-12s  %-30s  driver=%-20s  %s\n" "$node" "${id:-unknown}" "$driver" "${name:-}"
    done
else
    echo "(no hidraw devices found)"
fi

section "hidraw Ownership (which process has each node open)"
if have lsof; then
    lsof /dev/hidraw* 2>/dev/null | awk 'NR==1 || $1!="COMMAND"' | head -40
elif have fuser; then
    fuser -v /dev/hidraw* 2>/dev/null
else
    echo "(skipped: neither lsof nor fuser found — install lsof)"
fi

section "input/event Ownership (evdev devices)"
if have fuser; then
    fuser -v /dev/input/event* 2>/dev/null | head -20
elif have lsof; then
    lsof /dev/input/event* 2>/dev/null | head -20
else
    echo "(skipped: fuser/lsof not found)"
fi

section "USB Bus Device Ownership"
if have lsof; then
    lsof /dev/bus/usb/*/* 2>/dev/null | awk '{print $1, $2, $9}' | sort -u | head -30
else
    echo "(skipped: lsof not found)"
fi

section "Kernel Driver Bindings (sysfs)"
for h in /sys/class/hidraw/hidraw*; do
    [ -e "$h" ] || continue
    node=$(basename "$h")
    if have udevadm; then
        driver=$(udevadm info "/dev/$node" 2>/dev/null | grep "DRIVER=" | head -1 | cut -d= -f2)
        subsystem=$(udevadm info "/dev/$node" 2>/dev/null | grep "SUBSYSTEM=" | head -1 | cut -d= -f2)
        printf "  /dev/%-12s  subsystem=%-10s  driver=%s\n" "$node" "${subsystem:-?}" "${driver:-none}"
    fi
done

section "Recent USB Kernel Messages"
if have journalctl; then
    journalctl -k --since "10 minutes ago" 2>/dev/null | grep -iE 'usb|hid' | tail -20
elif [ -r /var/log/kern.log ]; then
    grep -iE 'usb|hid' /var/log/kern.log | tail -20
else
    echo "(skipped: journalctl not available)"
fi

printf '\nDone. Interpret with usb-peripheral-debugger/references/device-ownership.md\n'
