#!/bin/sh
# rgb-audit.sh — active RGB tools, claimed interfaces, conflict summary
# Read-only. Produces a one-line verdict per device.
LC_ALL=C

have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n=== %s ===\n' "$1"; }

section "OpenRGB"
if pgrep -x openrgb >/dev/null 2>&1; then
    echo "  RUNNING (PID: $(pgrep -x openrgb | tr '\n' ' '))"
    if have lsof; then
        echo "  Open devices:"
        lsof -p "$(pgrep -x openrgb | tr '\n' ',')" 2>/dev/null \
            | grep '/dev/hidraw\|/dev/bus/usb' | awk '{print "    " $9}' | sort -u
    fi
else
    echo "  not running"
fi

section "openrazer (kernel module + daemon)"
razer_mods=$(lsmod 2>/dev/null | grep -E '^razer' | awk '{print $1}' | tr '\n' ' ')
if [ -n "$razer_mods" ]; then
    echo "  Kernel modules loaded: $razer_mods"
else
    echo "  No razer kernel modules loaded"
fi
if have systemctl; then
    openrazer_state=$(systemctl --user is-active openrazer 2>/dev/null)
    echo "  Daemon (openrazer.service): $openrazer_state"
fi

section "Solaar"
if pgrep -x solaar >/dev/null 2>&1; then
    echo "  RUNNING (PID: $(pgrep -x solaar | tr '\n' ' '))"
    if have lsof; then
        echo "  Open devices:"
        lsof -p "$(pgrep -x solaar | tr '\n' ',')" 2>/dev/null \
            | grep '/dev/hidraw\|/dev/bus/usb' | awk '{print "    " $9}' | sort -u
    fi
else
    echo "  not running"
fi

section "trccd (Thermalright TRCC)"
trccd_count=$(pgrep -c trccd 2>/dev/null || echo 0)
if [ "$trccd_count" -gt 0 ] 2>/dev/null; then
    if [ "$trccd_count" -gt 1 ]; then
        echo "  WARNING: $trccd_count instances running — possible fork-bomb"
        echo "  See: examples/thermalright-trcc.md"
    else
        echo "  RUNNING (1 instance — healthy)"
    fi
    if have lsof; then
        echo "  Open devices:"
        lsof -p "$(pgrep trccd | tr '\n' ',')" 2>/dev/null \
            | grep '/dev/hidraw\|/dev/bus/usb' | awk '{print "    " $9}' | sort -u
    fi
else
    echo "  not running"
fi

section "ratbagd / Piper"
if pgrep -x ratbagd >/dev/null 2>&1; then
    echo "  ratbagd RUNNING"
else
    echo "  ratbagd not running"
fi

section "hidraw Interface Ownership Summary"
if have lsof; then
    printf "  %-20s %-10s %s\n" "Device" "PID" "Process"
    printf "  %-20s %-10s %s\n" "------" "---" "-------"
    lsof /dev/hidraw* 2>/dev/null | awk 'NR>1 {printf "  %-20s %-10s %s\n", $9, $2, $1}' | sort -k1

    # Conflict detection: multiple processes on same hidraw
    echo ""
    echo "  Conflict check:"
    lsof /dev/hidraw* 2>/dev/null | awk 'NR>1 {print $9}' | sort | uniq -d | while read node; do
        procs=$(lsof "$node" 2>/dev/null | awk 'NR>1 {print $1 "/" $2}' | tr '\n' '  ')
        echo "  CONFLICT: $node claimed by: $procs"
    done
    # If no conflicts found:
    conflicts=$(lsof /dev/hidraw* 2>/dev/null | awk 'NR>1 {print $9}' | sort | uniq -d | wc -l)
    [ "$conflicts" -eq 0 ] && echo "  OK: no hidraw conflicts detected (each node has at most one opener)"
else
    echo "(skipped: lsof not found — install lsof)"
fi

printf '\nDone. Interpret with usb-peripheral-debugger/references/rgb-control.md\n'
