#!/bin/sh
# audio-snapshot.sh — read-only audio stack snapshot: server identity, service
# state, sinks/sources/defaults, ALSA cards, bridge-package presence. Mutates nothing.

LC_ALL=C; export LC_ALL   # stable output for parsing regardless of system locale

have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n=== %s ===\n' "$1"; }

section "audio server identity"
if have pactl; then
    pactl info 2>/dev/null | grep -E 'Server Name|Server Version|Default Sink|Default Source' \
        || echo "(pactl could not connect — no audio server running for this user?)"
else
    echo "(skipped: pactl not found — install libpulse)"
fi

section "PipeWire / WirePlumber service state"
if have systemctl; then
    for u in pipewire.service pipewire-pulse.service wireplumber.service; do
        state=$(systemctl --user is-active "$u" 2>/dev/null)
        printf '%-26s %s\n' "$u" "${state:-unknown}"
    done
else
    echo "(skipped: systemctl not found)"
fi

section "sinks (outputs)"
if have wpctl; then
    wpctl status 2>/dev/null | sed -n '/Sinks:/,/Sources:/p'
elif have pactl; then
    pactl list short sinks 2>/dev/null || echo "(no sinks listed)"
else
    echo "(skipped: no wpctl/pactl)"
fi

section "sources (inputs)"
if have pactl; then
    pactl list short sources 2>/dev/null || echo "(no sources listed)"
fi

section "ALSA cards"
if [ -r /proc/asound/cards ]; then
    cat /proc/asound/cards
else
    echo "(no /proc/asound/cards — ALSA not present?)"
fi
if have aplay; then
    echo
    aplay -l 2>/dev/null | grep -E '^card' || echo "(aplay lists no playback devices)"
fi

section "bridge/compat package presence (Arch package names)"
if have pacman; then
    for p in pipewire pipewire-pulse pipewire-alsa pipewire-jack wireplumber lib32-pipewire; do
        if pacman -Qq "$p" >/dev/null 2>&1; then
            echo "installed:  $p"
        else
            echo "MISSING:    $p"
        fi
    done
    echo "(note: pipewire-alsa missing = no audio in FMOD games; lib32-pipewire missing = no 32-bit game audio)"
else
    echo "(skipped: pacman not found — check your distro's equivalents of pipewire-alsa / lib32-pipewire)"
fi

section "user wireplumber overrides"
d="$HOME/.config/wireplumber/wireplumber.conf.d"
if [ -d "$d" ]; then
    ls -l "$d"
else
    echo "(none — $d does not exist)"
fi

echo
echo "Done. Interpret with steam-debugger reference/audio.md failure table."
