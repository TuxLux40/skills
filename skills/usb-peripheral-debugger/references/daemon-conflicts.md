# Daemon Conflicts

Detecting and resolving contention between multiple services that claim the same USB device.

---

## Detection

### Which USB-related daemons are active?

```bash
systemctl --user list-units --type=service --state=running \
  | grep -iE 'razer|logitech|solaar|rgb|piper|ratbag|trcc|hid|input|usb'

# Also check system-level services:
systemctl list-units --type=service --state=running \
  | grep -iE 'razer|logitech|solaar|rgb|piper|ratbag|trcc|hid|input|usb'
```

### Which processes have USB/HID devices open?

```bash
# All hidraw openers:
lsof /dev/hidraw* 2>/dev/null

# All USB bus device openers:
lsof /dev/bus/usb/*/* 2>/dev/null | head -40

# Combined + PID lookup:
lsof /dev/hidraw* /dev/bus/usb/*/* 2>/dev/null | awk '{print $1, $2, $NF}' | sort -u
```

### Watch for conflict errors in real time

```bash
journalctl -f --user | grep -iE 'busy|ebusy|failed|conflict|hidraw|hid.*error'
dmesg -w | grep -iE 'usb.*error|hid.*error|failed to|busy'
```

---

## Conflict Resolution Matrix

| Device type | Recommended single owner | What to disable |
|---|---|---|
| RGB keyboard / mouse (RGB only) | OpenRGB | openrazer (if Razer), solaar (if Logitech) |
| Logitech device (DPI/macro also needed) | Solaar | OpenRGB for that device |
| Razer device (effects + macros) | openrazer + Polychromatic | OpenRGB for that device |
| Logitech device (onboard profile written) | None (profile in firmware) | Solaar + OpenRGB can both be off |
| Thermalright LCD cooler | trccd.service (systemd) | Any XDG autostart variant of trccd |
| Gaming mouse (DPI config) | ratbagd / Piper | OpenRGB (check if OpenRGB has it first) |

**General principle:** pick one tool per device. Document which tool owns which device so it's reproducible.

---

## Systemd Safe-Start Rule

Systemd services start with a **clean environment** (no inherited shell vars). This is the correct way to start any daemon that reads environment variables as control signals.

Wrong (inherits shell env → may cause fork-bomb or unexpected behavior):
```bash
# From a terminal or script that inherited login env:
trccd          # BAD if env has sentinel var set
openrgb --server &   # less critical but still sloppy
```

Right:
```bash
systemctl --user start trccd.service      # clean env
systemctl --user start openrazer          # clean env
```

**For any daemon: prefer systemd user service over manual background process.**

---

## The Environment-Variable Fork-Bomb Pattern

This pattern affects any daemon that uses an env var to signal "I am already running" — instead of checking a socket or PID file.

**How it breaks:**
1. Daemon sets `export SENTINEL_VAR=1` in `/etc/profile.d/something.sh` (so CLI tools route through it)
2. User starts a daemon manually or via a script that inherited the login shell environment
3. Daemon's `run_daemon()` function checks `os.environ.get('SENTINEL_VAR')` — finds it set
4. Before the daemon has bound its socket, it calls `ensure_daemon()` to "connect to existing daemon"
5. `ensure_daemon()` spawns another instance → which also sees `SENTINEL_VAR=1` → spawns again → infinite chain

**Fix template (Python):**
```python
def run_daemon():
    # Clear the sentinel var BEFORE checking socket — prevents fork-bomb
    # when spawned from a process that inherited the login env
    os.environ.pop('SENTINEL_VAR', None)
    
    # Now proceed with socket binding + normal startup
    bind_socket()
    ...
```

**Fix template (shell/systemd service file):**
```ini
[Service]
Environment=SENTINEL_VAR=
# or:
ExecStart=/usr/bin/env -u SENTINEL_VAR /usr/bin/mydaemon
```

**Diagnostic — is this happening?**
```bash
# Check if a sentinel var is set in current shell:
env | grep -iE 'daemon|running|socket|pid' | grep -v PATH

# Check if trccd (or similar) is spawning multiple instances:
pgrep -la trccd
# or:
pgrep -c trccd   # count — should be 1
```

See `examples/thermalright-trcc.md` for the specific TRCC case where this was found and fixed (fix accepted upstream).

---

## Disabling Conflicting Services

```bash
# Stop + disable a user service for this session and future boots:
systemctl --user disable --now SERVICE_NAME

# Stop only for this session (re-enables on next login):
systemctl --user stop SERVICE_NAME

# Check if a service is enabled (will start on login):
systemctl --user is-enabled SERVICE_NAME

# List all enabled user services:
systemctl --user list-unit-files --type=service --state=enabled
```

### Stopping XDG autostart entries

Some daemons use XDG autostart (`.desktop` files in `~/.config/autostart/` or `/etc/xdg/autostart/`) instead of systemd. These start with the desktop session and may inherit the login environment.

```bash
# Find autostart entries for a daemon (example: trccd):
find ~/.config/autostart /etc/xdg/autostart -name '*trcc*' 2>/dev/null

# Disable by adding Hidden=true:
echo "[Desktop Entry]
Hidden=true" > ~/.config/autostart/app-trcc-linux@autostart.desktop

# Or delete the autostart file entirely (if you manage via systemd instead):
rm ~/.config/autostart/app-trcc-linux@autostart.desktop
```

---

## Preventing Conflicts: udev-Based Ordering

If two tools must both interact with the same device (e.g., Solaar for receiver management AND OpenRGB for RGB), use udev rules to ensure they don't both grab hidraw at the same time:

```bash
# Check which interface is needed by each tool:
# - Solaar needs: receiver management interface (often hidraw1 on Bolt)
# - OpenRGB needs: keyboard HID interface (often hidraw0 on Bolt)
# If they use DIFFERENT interfaces, both can run safely
```

Verify with:
```bash
# Run both, then check if writes succeed:
lsof /dev/hidraw* 2>/dev/null
# Each should show exactly one opener per node
```

If they both need the same interface, you must choose one.
