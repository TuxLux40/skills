---
name: yubikey-linux-setup
description: >
  Use this skill whenever the user mentions YubiKey, hardware security key,
  2FA on Linux, PAM authentication with physical token, FIDO2/U2F on Linux,
  pam-u2f, smart card on Linux, PIV certificates, OATH/TOTP on hardware,
  OpenPGP on hardware key, pcscd, ykman, yubico-piv-tool, pamu2fcfg,
  or wants to protect SSH/sudo/login with a physical token. Also trigger for
  "passwordless login Linux", "hardware token Linux", "security key Linux",
  "sudo with YubiKey", "YubiKey PAM", "FIDO2 Linux auth", "browser client cert",
  "pcsc", "scdaemon", "gpg card", "oct tool", "openpgp card". Trigger even when
  user doesn't say "YubiKey" but clearly needs hardware-backed auth on Linux.
---

# YubiKey Linux Setup

Full guide: udev → packages → pcscd → PAM/PIV/features.
Caveman mode active. Preserve all commands verbatim.

## Quick Decision Tree

```
What need?
├── First-time setup (new key, fresh system) → Step 0–3 below
│
├── PROCEDURES (step-by-step, goal-oriented)
│   ├── Require touch for sudo/login → procedures/sudo-2fa.md
│   ├── SSH login with PIV cert (no key file) → procedures/ssh-piv.md
│   ├── TOTP codes from CLI (replace phone app) → procedures/oath-totp.md
│   ├── Move/generate GPG key on card → procedures/openpgp-setup.md
│   └── Browser client cert auth (Firefox/Chromium) → procedures/browser-smartcard.md
│
└── REFERENCE (command lookup, details, edge cases)
    ├── PAM config: pamu2fcfg options, all service files → references/pam-integration.md
    ├── PIV: all yubico-piv-tool commands, slots, attestation → references/piv-management.md
    ├── ykman: FIDO2, OTP, OATH, OpenPGP, FIPS, YubiHSM 2 → references/feature-management.md
    ├── scdaemon, pcscd conflicts, polkit, WKD, CCID arch → references/openpgp-scdaemon.md
    └── All URLs, crawler status → references/references.md
```

## Step 0: Identify Device

```bash
ykman info
lsusb | grep -i yubico
```

No `ykman`? Install first (Step 2).

Output includes: serial, firmware version, form factor, enabled interfaces.
Firmware version matters — determines available features. See feature table in `references/feature-management.md`.

## Step 1: udev Rules (Required — Do First)

Without these: FIDO2 needs root; OTP broken for non-root; smart card unreliable.

### OTP / Smart Card — `69-yubikey.rules`

```bash
sudo tee /etc/udev/rules.d/69-yubikey.rules << 'EOF'
ACTION!="add|change", GOTO="yubico_end"

# Yubico Yubikey II
ATTRS{idVendor}=="1050", ATTRS{idProduct}=="0010|0110|0111|0114|0116|0401|0403|0405|0407|0410", \
    ENV{ID_SECURITY_TOKEN}="1"

LABEL="yubico_end"
EOF
```

### FIDO2 / U2F — `70-u2f.rules`

```bash
sudo tee /etc/udev/rules.d/70-u2f.rules << 'EOF'
ACTION!="add|change", GOTO="u2f_end"

# Yubico YubiKey
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1050", ATTRS{idProduct}=="0113|0114|0115|0116|0120|0121|0200|0402|0403|0406|0407|0410", TAG+="uaccess", GROUP="plugdev", MODE="0660"

LABEL="u2f_end"
EOF
```

### Activate Rules

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

User must be in `plugdev` group (re-login after):
```bash
sudo usermod -aG plugdev $USER
```

Upstream canonical rule files:
- OTP: https://github.com/Yubico/yubikey-personalization/blob/master/69-yubikey.rules
- FIDO2: https://github.com/Yubico/libu2f-host/blob/master/70-u2f.rules

## Step 2: Packages

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install yubikey-manager libpam-u2f pamu2fcfg yubico-piv-tool pcscd
```

Yubico PPA (newer versions):
```bash
sudo add-apt-repository ppa:yubico/stable && sudo apt update
```

### Fedora/RHEL

```bash
sudo dnf install yubikey-manager pam-u2f pamu2fcfg yubico-piv-tool pcsc-lite
```

### Arch Linux

```bash
sudo pacman -S yubikey-manager pam-u2f yubico-piv-tool ccid opensc
```

ykman also installable via pip: `pip install yubikey-manager`

## Step 3: pcscd Smart Card Daemon

Required for: PIV, OpenPGP, OATH, HSMAuth.
Not needed for: FIDO2-only, OTP.

```bash
sudo systemctl enable --now pcscd
systemctl status pcscd
```

GnuPG conflict? scdaemon fights pcscd for card access:
```bash
gpg-connect-agent killagent /bye
```

## Interface Access Summary

| Interface | Daemon | udev file |
|-----------|--------|-----------|
| FIDO2/U2F | none | 70-u2f.rules |
| OTP (keyboard) | none | 69-yubikey.rules |
| PIV (smart card) | pcscd | 69-yubikey.rules |
| OpenPGP | pcscd | 69-yubikey.rules |
| OATH | pcscd | 69-yubikey.rules |
| HSMAuth | pcscd | 69-yubikey.rules |

## Files

| File | When to read |
|------|-------------|
| `procedures/sudo-2fa.md` | Step-by-step: sudo/login touch 2FA |
| `procedures/ssh-piv.md` | Step-by-step: SSH via PIV cert |
| `procedures/oath-totp.md` | Step-by-step: TOTP from CLI |
| `procedures/openpgp-setup.md` | Step-by-step: GPG key on card, oct tool, SSH via GPG |
| `procedures/browser-smartcard.md` | Step-by-step: Firefox/Chromium PKCS#11, p11-kit |
| `references/pam-integration.md` | All pamu2fcfg/pam_u2f.so options, every PAM service file |
| `references/piv-management.md` | All yubico-piv-tool commands, slots, attestation |
| `references/feature-management.md` | ykman full reference: FIDO2, OTP, OATH, FIPS, YubiHSM 2 |
| `references/openpgp-scdaemon.md` | scdaemon config, pcscd conflicts, polkit, WKD, CCID arch |
| `references/references.md` | URLs, crawler accessibility status |

## Search for Unknown Info

When info not in reference files:

1. Check what search MCPs or plugins are available (e.g., Tavily, Brave, Firecrawl, Perplexity, etc.). Use whichever is active in the current session — don't assume a specific one.
2. Fallback: invoke `firecrawl-scrape` skill or `agent-browser` skill to fetch specific URLs directly.
3. Start from curated links in `references/references.md` — organized for both humans and agents.

## Diagnostics

```bash
# Identify key and firmware
ykman info
lsusb | grep -i yubico

# Scan smart card readers and cards (pcsc-tools)
pcsc_scan           # shows ATR + card events; confirm pcscd sees YubiKey

# Check pcscd
systemctl status pcscd

# Check FIDO2 access
fido2-token -L      # needs libfido2-utils

# Kill scdaemon (releases card if GnuPG holds it)
gpgconf --kill scdaemon
```

## Common First-Time Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Access denied` on FIDO2 | Missing udev or not in plugdev | Add 70-u2f.rules; `usermod -aG plugdev $USER`; re-login |
| `No reader found` / pcscd error | pcscd not running | `systemctl start pcscd` |
| `No YubiKey found` in ykman | USB permissions or pcscd conflict | Check `lsusb`; restart pcscd; unplug/replug |
| OTP outputs garbage characters | Wrong keyboard layout mapped | Use ykman to check OTP config; set layout |
| GPG card not found | scdaemon conflicts with pcscd | `gpgconf --kill scdaemon` |
| `LIBUSB_ERROR_BUSY` | GnuPG holds exclusive USB access | `gpgconf --kill scdaemon`; configure pcscd mode |

## Safety Warning — PAM

**Before editing any PAM file: open a root terminal and keep it open until you verify the change works. A broken PAM config locks you out of the system entirely.**

Always backup before editing:
```bash
sudo cp /etc/pam.d/sudo /etc/pam.d/sudo.bak
```

Full PAM guidance in `references/pam-integration.md`.
