# Procedure: YubiKey Touch for sudo (2FA)

**Goal:** Physical YubiKey touch required for every `sudo` command.
**Time:** ~10 min
**Requires:** udev rules installed (Step 1 in SKILL.md), key plugged in

---

## Prerequisites

```bash
# Verify key detected
ykman info

# Verify plugdev membership
groups $USER | grep plugdev   # if missing: sudo usermod -aG plugdev $USER && re-login
```

---

## Procedure

### 1 — Install pam-u2f

```bash
# Debian/Ubuntu
sudo apt install libpam-u2f pamu2fcfg

# Fedora/RHEL
sudo dnf install pam-u2f pamu2fcfg

# Arch
sudo pacman -S pam-u2f
```

### 2 — Register key

```bash
# Single user (stores in ~/.config/Yubico/u2f_keys)
pamu2fcfg > ~/.config/Yubico/u2f_keys

# System-wide (required for sudo — runs as root)
mkdir -p /etc/security/u2f_keys.d
pamu2fcfg -u $USER | sudo tee /etc/u2f_mappings

# Add backup key (run while first key is still plugged in, then plug in backup)
pamu2fcfg -n -u $USER | sudo tee -a /etc/u2f_mappings
```

### 3 — Open a root terminal BEFORE editing PAM

**Critical: keep this open until verified. A broken PAM config locks you out.**

```bash
sudo -s   # keep this terminal open
```

### 4 — Backup sudo PAM file

```bash
sudo cp /etc/pam.d/sudo /etc/pam.d/sudo.bak
```

### 5 — Add YubiKey to sudo PAM

```bash
sudo nano /etc/pam.d/sudo
```

Add this line **after** `@include common-auth` (Ubuntu) or `auth include system-auth` (Fedora/Arch):

```
auth required pam_u2f.so authfile=/etc/u2f_mappings cue
```

Options used:
- `authfile=` — shared mappings file (required when registered as root)
- `cue` — prints "Please touch your authenticator device" prompt
- `nouserok` — add this if some users don't have keys (they skip the check)

Full line for shared system with mixed users:
```
auth required pam_u2f.so authfile=/etc/u2f_mappings cue nouserok
```

### 6 — Verify in new terminal (keep root terminal open)

```bash
# Open NEW terminal (not the root one)
sudo echo "works"
# Should prompt for password, then print touch prompt, then succeed
```

If this fails:
- **Restore from root terminal:** `cp /etc/pam.d/sudo.bak /etc/pam.d/sudo`
- See Troubleshoot section below

### 7 — Remove backup (only after verifying)

```bash
sudo rm /etc/pam.d/sudo.bak
```

---

## Verify

```bash
sudo -k              # clear sudo timestamp
sudo echo "test"     # should require password + touch
```

Expected flow: password prompt → "Please touch your authenticator device." → success.

---

## Common PAM Stack Variants

### 2FA (password + touch) — most secure

```
auth required pam_u2f.so authfile=/etc/u2f_mappings cue
```
Place after `@include common-auth` or equivalent.

### Touch-only, no password (passwordless sudo with PIN on key)

```
auth sufficient pam_u2f.so authfile=/etc/u2f_mappings pinverification=1
auth required pam_u2f.so authfile=/etc/u2f_mappings
```

### Require either password OR touch (not both)

```
auth sufficient pam_u2f.so authfile=/etc/u2f_mappings cue
auth sufficient pam_unix.so nullok
auth required pam_deny.so
```

---

## Extend to Login and Screen Lock

Same pattern — edit service file, add `pam_u2f.so` line:

| Service | File |
|---------|------|
| Login (TTY) | `/etc/pam.d/login` |
| KDE lock | `/etc/pam.d/kde` or `/etc/pam.d/sddm` |
| GNOME lock | `/etc/pam.d/gnome-screensaver` or `/etc/pam.d/gdm-password` |
| su | `/etc/pam.d/su` |
| SSH | `/etc/pam.d/sshd` (also needs SSH config — see below) |

SSH requires additional config in `/etc/ssh/sshd_config`:
```
UsePAM yes
ChallengeResponseAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

---

## Troubleshoot

| Symptom | Cause | Fix |
|---------|-------|-----|
| Touch prompt never appears | `pam_u2f.so` line missing or wrong position | Check file syntax; confirm line exists |
| `Authentication failure` without prompt | Wrong `authfile` path or file permissions | `ls -la /etc/u2f_mappings`; must be readable by root |
| Works as user, fails for root sudo | Mapping stored only in `~/.config/Yubico/` | Re-register with `sudo pamu2fcfg -u $USER > /etc/u2f_mappings` |
| Locked out after bad edit | `pam_u2f.so` syntax error | Boot recovery shell, restore backup |
| SELinux denial (RHEL/Fedora) | CVE-2020-24612: silent bypass if SELinux blocks | `sudo setsebool -P authlogin_yubikey 1` |

Debug mode (adds verbose log):
```bash
auth required pam_u2f.so authfile=/etc/u2f_mappings cue debug debug_file=/var/log/pam_u2f.log
```

Test without changing system PAM:
```bash
sudo apt install pamtester   # or equivalent
pamtester sudo $USER authenticate
```
