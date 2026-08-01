# Procedure: OATH/TOTP Codes on YubiKey

**Goal:** Store TOTP secrets on YubiKey, generate codes from CLI — replaces phone authenticator apps.
**Time:** ~5 min per account
**Requires:** pcscd running, ykman installed

---

## Prerequisites

```bash
# pcscd must be active (OATH uses CCID interface)
systemctl is-active pcscd || sudo systemctl enable --now pcscd

# ykman installed and sees key
ykman info
```

---

## Procedure

### 1 — Add a TOTP account

**Method A: From QR code URI (recommended)**

When a site shows a QR code, most let you also copy the `otpauth://` URI. Use that:

```bash
ykman oath accounts uri "otpauth://totp/GitHub:you@example.com?secret=JBSWY3DPEHPK3PXP&issuer=GitHub"
```

**Method B: From secret key directly**

```bash
# 6-digit, 30-second (standard defaults)
ykman oath accounts add --totp GitHub:you@example.com JBSWY3DPEHPK3PXP

# 8-digit, 60-second (some sites use this)
ykman oath accounts add --totp --digits 8 --period 60 SomeBank:me@bank.com SECRET

# Require touch to generate code (anti-malware):
ykman oath accounts add --totp --touch GitHub:you@example.com SECRET
```

### 2 — Generate a code

```bash
# Single account
ykman oath accounts code "GitHub:you@example.com"

# All accounts
ykman oath accounts code

# Pipe to clipboard (wl-clipboard / xclip)
ykman oath accounts code "GitHub:you@example.com" | awk '{print $2}' | wl-copy
```

### 3 — List all stored accounts

```bash
ykman oath accounts list
```

### 4 — Protect OATH storage with password (optional)

```bash
ykman oath access change   # set password
ykman oath access change -c  # clear password
```

---

## Verify

```bash
# Should show newly added account
ykman oath accounts list

# Should print 6-digit rotating code
ykman oath accounts code "GitHub:you@example.com"
```

Enter that code on the site's 2FA prompt — it should accept it.

---

## Common Sites — Workflow

### GitHub
1. Settings → Password and authentication → Two-factor authentication
2. Click "Set up using an app"
3. Click "Can't scan the QR code?" to reveal URI
4. `ykman oath accounts uri "<paste-uri>"`

### AWS
1. IAM → Users → Security credentials → Assigned MFA device
2. Virtual MFA → Show QR code → "Secret key" link reveals base32
3. `ykman oath accounts add --totp AWS:<username> <secret>`

### Google
1. myaccount.google.com → Security → 2-Step Verification
2. Authenticator app → Can't scan it? → shows secret
3. `ykman oath accounts add --totp Google:<email> <secret>`

---

## Manage Accounts

```bash
# Delete an account
ykman oath accounts delete "GitHub:you@example.com"

# Rename (delete + re-add)
ykman oath accounts delete "oldname"
ykman oath accounts add --totp "newname" <secret>

# Reset all OATH accounts (irreversible)
ykman oath reset
```

---

## Shell Integration

Add a helper for quick code generation:

```bash
# ~/.bashrc or ~/.zshrc
totp() { ykman oath accounts code "$1" | awk '{print $NF}'; }

# fish: ~/.config/fish/config.fish
function totp; ykman oath accounts code $argv | awk '{print $NF}'; end
```

Usage: `totp "GitHub:you@example.com"`

---

## Troubleshoot

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Failed to open device` | pcscd not running | `sudo systemctl start pcscd` |
| `Failed to open device` | GnuPG scdaemon locked card | `gpgconf --kill scdaemon` |
| Code rejected by site | Wrong time sync | `timedatectl status` — NTP must be synced |
| Code rejected | Wrong TOTP period/digits | Re-add with `--period 60` or `--digits 8` |
| `No account found` | Name mismatch | `ykman oath accounts list` to see exact name |
| OATH password set, forgot it | — | `ykman oath reset` (deletes all accounts) |
