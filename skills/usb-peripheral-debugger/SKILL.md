---
name: usb-peripheral-debugger
description: >
  Systematic debugging and configuration of USB HID peripherals on Linux: ownership detection,
  daemon conflict resolution, RGB tool arbitration (OpenRGB, openrazer, Solaar, Polychromatic),
  device-specific profile management, and USB protocol reverse engineering. Use whenever: a USB
  peripheral (keyboard, mouse, headset, soundbar, custom LCD, controller) isn't responding as
  expected; RGB lighting reverts or won't apply; two tools fight over the same device; you want to
  identify which daemon or process currently controls a device; you need to reverse-engineer a USB
  HID protocol to build Linux support; a peripheral daemon crashes or fork-bombs; or you want to
  consolidate to a single RGB controller. Works on any Arch-based distro (Arch, CachyOS, Manjaro,
  EndeavourOS) and any systemd distribution. Trigger even when the user just asks "what's
  controlling my USB device" or "why does my keyboard go back to rainbow" or "how do I capture USB
  traffic" — the skill is the right tool for all of these.
---

## Output Style

Drop filler words and hedging. Keep technical accuracy. Pattern: `[finding]. [cause]. [fix].`
Exception: spell out unfamiliar commands before using them. Never assume the user knows what
`udevadm`, `hidraw`, or `lsmod` are without a brief intro.

---

## File Map

| Reference file | Contents |
|---|---|
| `references/device-ownership.md` | USB stack anatomy, udev, hidraw, fuser/lsof ownership commands |
| `references/rgb-control.md` | OpenRGB, openrazer, Solaar, Polychromatic — daemon arbitration + single-controller strategy |
| `references/daemon-conflicts.md` | Detecting and resolving service contention; systemd-safe startup; env-var fork-bomb pattern |
| `references/reverse-engineering.md` | Full USB HID RE workflow: enumerate → capture → decode → replicate → document + firmware analysis |
| `references/examples/logitech-g915.md` | Case study: G915, Bolt receiver, onboard profiles, autostart workaround |
| `references/examples/razer-leviathan.md` | Case study: Leviathan V2 X, openrazer, Polychromatic RE path |
| `references/examples/thermalright-trcc.md` | Case study: TRCC daemon fork-bomb root cause and upstream fix |
| `references/tribal.md` | Sourced anecdotal fixes (URL + date + mechanism required) |
| `references/sources.md` | Research tool decision table and per-source access methods |

Scripts (read-only, gracefully degrade if tools are missing):

| Script | What it collects |
|---|---|
| `scripts/usb-ownership.sh` | USB tree, per-hidraw process owner, kernel driver bindings |
| `scripts/daemon-snapshot.sh` | Active USB-related daemons, their unit files, open device files |
| `scripts/rgb-audit.sh` | Active RGB tools, claimed interfaces, conflict summary |

---

## USB Control Stack

```
Hardware → xhci_hcd → usb-core → HID driver → udev
                                                  │
                                    /dev/hidrawN  ← EXCLUSIVE (conflict zone)
                                    /dev/input/   ← shared (safe)
                                                  │
                              Daemons: openrazer / solaar / trccd / openrgb
                                                  │
                              User tools: Polychromatic / Piper / OpenRGB GUI
```

Explain any layer in detail with visualizations and what abbreviations mean.

---

## Unifying Mental Model

Every USB peripheral conflict reduces to this pattern:

```
USB device
  └─ xhci_hcd → usb-core → HID driver
       └─ udev → /dev/hidrawN  (exclusive)
            └─ daemon A claims it (openrazer / solaar / trccd / openrgb)
                 └─ daemon B also tries → EBUSY or silent failure
                      └─ question: who is the arbiter, and who is the unexpected claimant?
```

**Diagnostic reflex:** "Who holds `/dev/hidrawN` right now, and what rejected the second claimant?"

Tools: `lsof /dev/hidraw*`, `fuser /dev/input/event*`, `udevadm monitor`, `journalctl -xe | grep -i hid`

Example conflict (two tools, one device):
```
G915 keyboard on Bolt receiver (046d:c547)
├── /dev/hidraw0  ← OpenRGB wants this (direct libusb claim)
├── /dev/hidraw1  ← Solaar wants this  (receiver management)
└── /dev/input/event3  ← kernel input layer (safe to share)
         ↑
  CONFLICT: OpenRGB + Solaar both open hidraw → last one wins
  Symptom:  profile writes silently ignored, rainbow revert
  Fix:      daemon-conflicts.md → single-controller strategy
```

---

## Triage Protocol

### Step 1 — Intake questions

Ask before running any commands:

1. Which device(s)? (model name + `lsusb` output, or just VID:PID if known — e.g., `046d:c547`)
2. What's the symptom? (RGB reverts / won't apply / daemon crashes / device unresponsive / no Linux support at all)
3. Which tools are currently installed or running? (`openrgb`, `openrazer`, `solaar`, `polychromatic`, `piper`, any custom daemons)
4. What changed before it broke? (package update, new tool installed, config edit, reboot, kernel update)
5. Onboard-profile issue or live-control issue? (does the device need a persistent firmware profile, or is real-time control enough?)
6. End goal: fix existing tool, consolidate to one RGB controller, or reverse-engineer protocol for missing Linux support?

### Step 2 — Symptom routing

| Symptom | Reference |
|---|---|
| RGB tool sets colour but reverts after disconnect / reboot | `rgb-control.md` → onboard profile section |
| Device falls back to rainbow / default animation | `rgb-control.md` → empty onboard slot section |
| Daemon crashes, respawns endlessly, or fork-bombs | `daemon-conflicts.md` → env-var sentinel section |
| Two tools fighting over same device / EBUSY errors | `daemon-conflicts.md` → conflict resolution matrix |
| "Which process owns this device right now?" | `device-ownership.md` → run `scripts/usb-ownership.sh` |
| No Linux support for device at all | `reverse-engineering.md` Phase 1 |
| USB traffic capture / protocol analysis | `reverse-engineering.md` Phase 2 |
| Build Polychromatic / OpenRGB plugin for a device | `reverse-engineering.md` Phase 5 + `rgb-control.md` |
| Unknown device / kernel not binding correct driver | `device-ownership.md` → udevadm section |
| Service starts wrong / env-var contamination | `daemon-conflicts.md` → systemd safe-start section |
| Keyboard profile lost on reboot | `rgb-control.md` → onboard profile; example in `examples/logitech-g915.md` |

### Step 3 — Match fix to user comfort

Apply fix tiers in order — never skip to 🔴 without exhausting ✅ and ⚠️ first:

- ✅ **Official** — kernel/udev/upstream documented; safe; no reversal needed
- ⚠️ **Community** — widely used and well-understood, not officially endorsed
- 🟣 **Tribal** — anecdotal; **always include source URL + date + suspected mechanism** before suggesting; if mechanism is unknown, say so
- 🔴 **Deep / risky** — modifies udev rules system-wide, patches packages, survives kernel updates poorly; **always describe the risk and ask for confirmation** before proceeding

---

## Running the Diagnostic Scripts

Run these first to get a full picture before suggesting fixes:

```bash
bash ~/.claude/skills/usb-peripheral-debugger/scripts/usb-ownership.sh
bash ~/.claude/skills/usb-peripheral-debugger/scripts/daemon-snapshot.sh
bash ~/.claude/skills/usb-peripheral-debugger/scripts/rgb-audit.sh
```

Scripts degrade gracefully — missing tools print `(skipped: tool not found)` rather than failing.

---

## Updating This Skill

When a fix is found online that isn't in these files:
1. Check `references/sources.md` for the right research tool to fetch it
2. Verify the fix works (or note unverified)
3. Add to `references/tribal.md` with: source URL, date, mechanism, confirmation status
4. If it becomes widely confirmed, promote to the appropriate core reference file
