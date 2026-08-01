# Tribal Knowledge

Sourced anecdotal fixes. Each entry requires: source URL + date + mechanism. Entries without provenance are not included.

On a rolling-release distro (Arch, CachyOS), fixes older than ~18 months should be verified — the underlying bug may have been fixed upstream.

When a fix here becomes officially documented or merged upstream, move it to the appropriate core reference file and remove it from tribal.md.

---

## Format

```
### [Device/Issue Name]
- **Fix:** what to do
- **Source:** URL to original report, forum post, or commit
- **Date:** YYYY-MM
- **Confirmations:** N (description of confirmation quality)
- **Mechanism:** why this works (or "unknown" if not confirmed)
- **Reversal:** how to undo
- **Status:** [active / superseded by X / verify on kernel >= Y]
```

---

## Entries

### TRCC Daemon Fork-Bomb (Thermalright LCD Cooler)
- **Fix:** Add `os.environ.pop('TRCC_DAEMON', None)` at top of `run_daemon()` in trcc-linux source; always start via `systemctl --user start trccd.service` (systemd clears env); disable XDG autostart variant
- **Source:** https://github.com/Lexonight1/thermalright-trcc-linux/issues/162
- **Date:** 2026-05
- **Confirmations:** Accepted upstream by repo owner; deployed in production
- **Mechanism:** `TRCC_DAEMON=1` in `/etc/profile.d/trcc.sh` is inherited by any child process; `run_daemon()` checked this var before binding socket → called `ensure_daemon()` → spawned another instance → infinite chain; clearing var before socket check breaks the cycle
- **Reversal:** N/A — fix is safe and correct
- **Status:** Promoted to `examples/thermalright-trcc.md`; upstreamed

---

*(Add new entries here as they are discovered. Include source URL, date, and mechanism — without these, the fix cannot be evaluated or trusted.)*
