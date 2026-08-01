# Case Study: Thermalright TRCC Daemon Fork-Bomb

Demonstrates the environment-variable sentinel fork-bomb pattern. Fix was submitted upstream and accepted by the repo owner.

Upstream issue: https://github.com/Lexonight1/thermalright-trcc-linux/issues/162

---

## Device

Thermalright Frozen Notte / Frozen Magic 360 CPU cooler with LCD temperature display. Controlled by `trccd` — a Python-based user daemon.

---

## The Problem

`trccd` fork-bombs — spawns infinite instances — when launched from any process that inherited the login shell environment.

### Symptom

```bash
pgrep -c trccd   # returns a large and growing number
# system load spikes, terminal unresponsive
```

### Root cause

**Step 1:** `/etc/profile.d/trcc.sh` sets `export TRCC_DAEMON=1` in the login shell. This is intentional — it signals to the `trcc` CLI that a daemon is running so CLI commands route through the daemon socket instead of talking to hardware directly.

**Step 2:** If any process that inherited the login environment spawns `trccd` (e.g., a script, an agent spawner, an honcho process, any shell-started background process), `run_daemon()` is called.

**Step 3:** At the top of `run_daemon()`, before binding the socket, the code calls `ensure_daemon()` to check if a daemon is already running.

**Step 4:** `ensure_daemon()` checks `os.environ.get('TRCC_DAEMON')` — finds it set to `1` — assumes a daemon is running — attempts to connect — finds no socket (because the daemon hasn't started yet) — falls through to spawn another `trccd` process.

**Step 5:** The new `trccd` process also has `TRCC_DAEMON=1` in its inherited environment → calls `ensure_daemon()` → spawns another → infinite chain.

### Why systemd doesn't have this problem

systemd services start with a **clean environment** (ExecStart gets a minimal env, not the login shell's). `TRCC_DAEMON` is not exported into systemd service environments. The daemon starts, binds its socket, then sets `TRCC_DAEMON=1` itself — but only in the process that actually needs it. No inheritance chain, no fork-bomb.

---

## The Fix

Accepted upstream: clear the sentinel variable at the top of `run_daemon()` before any socket checks.

```python
def run_daemon():
    # Pop the sentinel var so that if we were spawned from a process
    # that inherited the login env (where TRCC_DAEMON=1), we don't
    # immediately call ensure_daemon() and fork-bomb ourselves.
    os.environ.pop('TRCC_DAEMON', None)

    # Now proceed with normal startup: bind socket, start event loop, etc.
    ...
```

This fix is a one-liner. It's safe because `run_daemon()` is only called when the user explicitly starts the daemon — not when CLI commands are invoked.

---

## General Pattern

This same bug can affect any daemon that:
1. Sets an env var in a login shell profile to route CLI commands through the daemon
2. Reads that env var in `run_daemon()` before binding its socket
3. Can be spawned from a process that inherited the login environment

**Fix template for any language:**

Python: `os.environ.pop('SENTINEL_VAR', None)`

Bash: `unset SENTINEL_VAR`

systemd service: `Environment=SENTINEL_VAR=` (or `ExecStart=/usr/bin/env -u SENTINEL_VAR /path/to/daemon`)

---

## Correct Startup

Always start `trccd` via systemd:

```bash
# Stop the XDG autostart variant (it runs with inherited env on session start):
systemctl --user stop 'app-trcc\x2dlinux@autostart.service'
systemctl --user disable 'app-trcc\x2dlinux@autostart.service'

# Start via the systemd service (clean env):
systemctl --user enable --now trccd.service

# Verify one instance running:
pgrep -c trccd   # should be 1
systemctl --user status trccd.service
```

If both the XDG autostart and the systemd service are enabled, the XDG autostart fires first with dirty env → fork-bomb → the systemd service then also tries to start. Disable the autostart.

---

## Diagnosis Commands

```bash
# Is it fork-bombing right now?
pgrep -la trccd | wc -l   # more than 1 = fork-bomb in progress

# Kill all instances:
pkill -9 trccd

# Check env for the sentinel var:
env | grep TRCC

# Check XDG autostart status:
systemctl --user status 'app-trcc\x2dlinux@autostart.service'

# Check systemd service status:
systemctl --user status trccd.service
```
