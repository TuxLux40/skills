#!/bin/sh
# daemon-snapshot.sh — active USB-related daemons, their unit files, open device files
# Read-only. Degrades gracefully if tools are missing.
LC_ALL=C

have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n=== %s ===\n' "$1"; }

KEYWORDS='razer|logitech|solaar|rgb|openrgb|piper|ratbag|trcc|hid|trccd|polychromatic|ckb|corsair|steelseries|hyperx'

section "Active User Services (USB/HID related)"
if have systemctl; then
    systemctl --user list-units --type=service --state=running 2>/dev/null \
        | grep -iE "$KEYWORDS" \
        || echo "  (none matching: $KEYWORDS)"
else
    echo "(skipped: systemctl not found)"
fi

section "Active System Services (USB/HID related)"
if have systemctl; then
    systemctl list-units --type=service --state=running 2>/dev/null \
        | grep -iE "$KEYWORDS" \
        || echo "  (none matching)"
else
    echo "(skipped)"
fi

section "XDG Autostart Entries (USB/HID related)"
for dir in "$HOME/.config/autostart" /etc/xdg/autostart; do
    [ -d "$dir" ] || continue
    found=$(find "$dir" -name '*.desktop' 2>/dev/null \
        | xargs grep -liE "$KEYWORDS" 2>/dev/null)
    if [ -n "$found" ]; then
        echo "  In $dir:"
        for f in $found; do
            enabled=$(grep -i 'Hidden=true' "$f" >/dev/null 2>&1 && echo "DISABLED" || echo "ENABLED")
            printf "    %-40s  %s\n" "$(basename "$f")" "$enabled"
        done
    fi
done
echo "  (check above — XDG autostart entries inherit login env; may conflict with systemd services)"

section "Environment Sentinel Variables (fork-bomb indicators)"
printf "  Current env vars that could act as daemon sentinels:\n"
env 2>/dev/null | grep -iE 'daemon|running|socket|_pid|_lock|trcc|razer|solaar|rgb' \
    | grep -v 'PATH\|MANPATH\|XDG\|SSH\|TERM' \
    || echo "  (none found)"

section "Open USB/HID Files per Process"
if have lsof; then
    lsof /dev/hidraw* /dev/bus/usb/*/* 2>/dev/null \
        | awk 'NR==1 || $1!="COMMAND"' \
        | sort -k1 \
        | head -50
elif have fuser; then
    echo "hidraw:"
    fuser -v /dev/hidraw* 2>/dev/null
else
    echo "(skipped: lsof/fuser not found)"
fi

section "Unit File Details (ExecStart for matched services)"
if have systemctl; then
    services=$(systemctl --user list-units --type=service --state=running 2>/dev/null \
        | grep -iE "$KEYWORDS" | awk '{print $1}')
    for svc in $services; do
        printf "\n  -- %s --\n" "$svc"
        systemctl --user cat "$svc" 2>/dev/null \
            | grep -E 'ExecStart|ExecStartPre|Environment|EnvironmentFile' \
            || echo "  (unit file not readable)"
    done
    [ -z "$services" ] && echo "  (no matching services to inspect)"
fi

section "Process Environment Check (sentinel var inheritance)"
if have lsof && have ps; then
    # Find pids of USB/HID related processes
    pids=$(ps aux 2>/dev/null | grep -iE "$(echo "$KEYWORDS" | tr '|' '\n' | head -5 | tr '\n' '|')x" \
        | grep -v grep | awk '{print $2}' | head -10)
    for pid in $pids; do
        cmd=$(ps -p "$pid" -o comm= 2>/dev/null)
        sentinel=$(cat "/proc/$pid/environ" 2>/dev/null | tr '\0' '\n' \
            | grep -iE 'daemon|trcc|razer|sentinel' | head -3)
        printf "  PID %-6s %-20s  env: %s\n" "$pid" "$cmd" "${sentinel:-(none)}"
    done
    [ -z "$pids" ] && echo "  (no matching processes found)"
fi

printf '\nDone. Interpret with usb-peripheral-debugger/references/daemon-conflicts.md\n'
