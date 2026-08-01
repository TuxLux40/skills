#!/bin/sh
# diagnose-session.sh — read-only evidence collector for gamescope session issues.
# Collects logind/seat state, DRM holders, session target state, and journal
# signatures of known failure patterns. Mutates nothing.

LC_ALL=C; export LC_ALL   # stable output for parsing regardless of system locale

have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n=== %s ===\n' "$1"; }

section "logind sessions"
if have loginctl; then
    loginctl list-sessions --no-pager 2>/dev/null
    printf '\nLinger state: '
    loginctl show-user "$(id -un)" -p Linger 2>/dev/null
    # Seatless manager-class sessions are the classic DRM-denial trigger
    for s in $(loginctl list-sessions --no-legend 2>/dev/null | awk '{print $1}'); do
        loginctl show-session "$s" -p Id,Class,Seat,State 2>/dev/null | tr '\n' ' '
        printf '\n'
    done
else
    echo "(skipped: loginctl not found)"
fi

section "DRM device holders"
if [ -e /dev/dri ]; then
    ls -l /dev/dri/ 2>/dev/null
    if have fuser; then
        # fuser needs root to see other users' processes
        fuser -v /dev/dri/card* 2>&1 || echo "(fuser returned nothing — run with sudo for complete view)"
    else
        echo "(skipped: fuser not found — install psmisc)"
    fi
else
    echo "(no /dev/dri — no KMS-capable GPU driver loaded?)"
fi

section "gamescope session target/service state"
if have systemctl; then
    for t in gamescope-session.target gamescope-session-cachyos.target graphical-session.target; do
        state=$(systemctl --user is-active "$t" 2>/dev/null)
        printf '%-36s %s\n' "$t" "${state:-unknown}"
    done
    printf '\nFailed user units:\n'
    systemctl --user list-units --state=failed --no-legend --no-pager 2>/dev/null || echo "(none)"
else
    echo "(skipped: systemctl not found)"
fi

section "journal: gamescope boot outcome (current boot)"
if have journalctl; then
    journalctl -b 0 --no-pager 2>/dev/null \
        | grep -iE 'Started Gamescope|Could not open KMS|Device or resource busy|Failed to create backend|gamescope.*segfault|TakeDevice|DRM master' \
        | tail -40
    [ $? -ne 0 ] && echo "(no matches or journal not readable — try sudo)"
else
    echo "(skipped: journalctl not found)"
fi

section "runtime environment (current shell)"
env | grep -E '^(STEAM|LD_PRELOAD|LD_LIBRARY|PROTON|PRESSURE|WAYLAND_DISPLAY|DISPLAY|XDG_SESSION)' || echo "(no relevant vars set)"

section "user manager environment (what services inherit)"
if have systemctl; then
    systemctl --user show-environment 2>/dev/null \
        | grep -E '^(WAYLAND_DISPLAY|DISPLAY|XAUTHORITY|STEAM|LD_)' \
        || echo "(no display/steam vars leaked into user manager — good)"
fi

section "stale mounts (SLR/bwrap failure trigger)"
mount 2>/dev/null | grep -E 'autofs|cifs|nfs' || echo "(no network/auto mounts)"

echo
echo "Done. Interpret with steam-debugger SKILL.md → session-architecture.md failure patterns."
