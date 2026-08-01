# PAM Integration Reference

pam-u2f: PAM module for FIDO2/U2F hardware key auth.
Read when: setting up login, sudo, SSH, or screen lock with YubiKey.

**CRITICAL: Before any PAM edit, open new root terminal. Keep open until verified. Wrong config = full lockout. No exceptions.**

## Install

```bash
# Ubuntu/Debian
sudo apt install libpam-u2f pamu2fcfg

# Fedora/RHEL
sudo dnf install pam-u2f pamu2fcfg

# Arch
sudo pacman -S pam-u2f

# Yubico PPA (newest version)
sudo add-apt-repository ppa:yubico/stable && sudo apt update && sudo apt install libpam-u2f
```

Source: https://github.com/Yubico/pam-u2f
Docs: https://developers.yubico.com/pam-u2f/

## Register YubiKey

### Per-User (default: `~/.config/Yubico/u2f_keys`)

```bash
mkdir -p ~/.config/Yubico
pamu2fcfg > ~/.config/Yubico/u2f_keys
# Touch YubiKey when LED blinks
```

Add backup/second YubiKey:
```bash
pamu2fcfg -n >> ~/.config/Yubico/u2f_keys
```

`-n` flag: append mode (no username prefix, just registration data).

### System-Wide (`/etc/u2f_mappings`)

Needed for sudo/login where per-user files may not be readable.

```bash
# Register user 'alice'
sudo pamu2fcfg -u alice >> /etc/u2f_mappings

# Add backup key for alice
sudo pamu2fcfg -u alice -n >> /etc/u2f_mappings
```

Mapping file format:
```
alice:<keyhandle1>,<userkey1>,<cosetype>,<options>:<keyhandle2>,...
bob:<keyhandle1>,<userkey1>,...
```

### pamu2fcfg Options

| Option | Effect |
|--------|--------|
| `-u USERNAME` | Register for specific user |
| `-o pam://hostname` | FIDO2 relying party ID (origin, default: `pam://hostname`) |
| `-i pam://hostname` | FIDO2 appid (default: same as origin) |
| `-r` | Resident credential (stored on key, discoverable) |
| `-t ES256\|EDDSA\|RS256` | COSE type for credential (default: ES256) |
| `-N` | Require PIN during registration |
| `-V` | Require user verification (biometrics) |
| `-n` | Print registration data only (no username line, for appending) |
| `-d` | Debug output |

## pam_u2f.so Module Options

Full option reference for PAM config lines.

| Option | Default | Effect |
|--------|---------|--------|
| `authfile=FILE` | `~/.config/Yubico/u2f_keys` | Key mapping file location |
| `cue` | off | Print "Please touch your security key" |
| `interactive` | off | Show interactive message before checking device |
| `pinverification=1` | 0 | Require FIDO2 PIN |
| `userverification=1` | 0 | Require user verification (biometrics/PIN) |
| `nouserok` | off | Allow login if user has no key mappings |
| `openasuser` | off | Read authfile as target user, not root (for per-user files in sudo) |
| `debug` | off | Enable debug output to stderr |
| `debug_file=FILE` | stderr | Debug log path (file must exist) |
| `max_devices=N` | 24 | Max YubiKeys to try per user |
| `origin=STRING` | `pam://hostname` | FIDO2 RP ID override |
| `appid=STRING` | same as origin | U2F appid override |
| `expand` | off | Enable variable expansion (`%u`=username, `%%`=%) |
| `sshformat` | off | Use OpenSSH FIDO key format in authfile |
| `alwaysok` | off | Accept all logins (demo/presentation only — never production) |

## PAM Stack Patterns

### 2FA: Password + YubiKey (both required)

```
# /etc/pam.d/sudo
auth   required   pam_unix.so
auth   required   pam_u2f.so authfile=/etc/u2f_mappings cue
```

User enters password, then touches YubiKey.

### Passwordless: PIN Only

YubiKey FIDO2 PIN replaces password. Falls back to password if no key.

```
auth   sufficient   pam_u2f.so authfile=/etc/u2f_mappings cue pinverification=1
auth   required     pam_unix.so
```

### Passwordless: Biometrics + PIN Fallback

Try biometrics first, fall back to PIN, fall back to password.

```
auth   sufficient   pam_u2f.so authfile=/etc/u2f_mappings cue pinverification=0 userverification=1
auth   sufficient   pam_u2f.so authfile=/etc/u2f_mappings cue pinverification=1 userverification=0
auth   required     pam_unix.so
```

### Either Password OR YubiKey (not both)

```
auth   sufficient   pam_u2f.so authfile=/etc/u2f_mappings cue nouserok
auth   required     pam_unix.so try_first_pass
```

`nouserok` lets users without a registered key fall through to password.

## PAM Service Files by Use Case

| Use case | PAM file | Notes |
|----------|----------|-------|
| Console login | `/etc/pam.d/login` | Physical access |
| sudo | `/etc/pam.d/sudo` | Privilege escalation |
| SSH (PAM-based) | `/etc/pam.d/sshd` | Remote auth via PAM |
| GDM (GNOME login) | `/etc/pam.d/gdm-password` | GUI login screen |
| KDE screen lock | `/etc/pam.d/kde` | Unattended terminal |
| GNOME screen lock | `/etc/pam.d/gnome-screensaver` or `/etc/pam.d/kde` | Distro-dependent |
| su | `/etc/pam.d/su` | User switching |

## Sudo with YubiKey

Always backup first:
```bash
sudo cp /etc/pam.d/sudo /etc/pam.d/sudo.bak
```

Edit `/etc/pam.d/sudo` — add pam_u2f.so line:
```
auth   required   pam_unix.so
auth   required   pam_u2f.so authfile=/etc/u2f_mappings cue
```

Test (keep root shell open!):
```bash
sudo echo "test"
# Prompts for password, then: "Please touch your security key"
```

Note: on systems using `pam_sudo_rule.so` or `pam_systemd.so`, place pam_u2f.so after existing auth lines.

## SSH + PAM U2F (Touch Required at Login)

SSH must use PAM for keyboard-interactive auth.

```bash
# /etc/ssh/sshd_config
UsePAM yes
ChallengeResponseAuthentication yes
# For key + touch combo:
AuthenticationMethods publickey,keyboard-interactive
```

Edit `/etc/pam.d/sshd`:
```
auth   required   pam_unix.so
auth   required   pam_u2f.so authfile=/etc/u2f_mappings cue
```

Restart sshd:
```bash
sudo systemctl restart sshd
```

Keep SSH session alive while testing new sessions.

## Screen Lock

### KDE Plasma

```
# /etc/pam.d/kde
auth   required   pam_unix.so
auth   required   pam_u2f.so authfile=/etc/u2f_mappings cue
```

### GNOME (Ubuntu/Fedora)

Distro-specific file — check which one exists:
```bash
ls /etc/pam.d/ | grep -E 'gnome|gdm|screensaver|polkit'
```

Common files: `/etc/pam.d/gnome-screensaver`, `/etc/pam.d/gdm-password`

```
auth   required   pam_unix.so
auth   required   pam_u2f.so authfile=/etc/u2f_mappings cue
```

Test by locking screen (Super+L), then unlocking.

## Debug Mode

Test without modifying live service config.

```bash
# Install pamtester
sudo apt install pamtester  # Debian/Ubuntu
sudo pamtester -v sudo $USER authenticate

# Temporary debug in PAM config
auth required pam_u2f.so authfile=/etc/u2f_mappings debug debug_file=/tmp/pam_u2f.log

# Watch log
touch /tmp/pam_u2f.log
tail -f /tmp/pam_u2f.log
```

Remove `debug debug_file=...` after diagnosing. Debug file must pre-exist.

## Lockout Recovery

Locked out due to bad PAM config? Options:

**Option 1:** Boot to recovery mode (if available):
```bash
# At GRUB: select recovery mode → root shell
nano /etc/pam.d/sudo
# Restore backup or remove bad line
```

**Option 2:** Boot live USB:
```bash
mount /dev/sdXY /mnt
arch-chroot /mnt  # or chroot /mnt /bin/bash
nano /etc/pam.d/sudo
```

**Option 3:** If another user with sudo access exists, use that session.

Prevention: always keep root terminal open during PAM changes. Test in new terminal before closing current session.

## SELinux Compatibility (RHEL/Fedora)

CVE-2020-24612: pam-u2f may fail silently on SELinux-enforcing systems.
Reference: https://access.redhat.com/security/cve/CVE-2020-24612

Diagnose:
```bash
ausearch -m avc -ts recent | grep pam_u2f
```

Fix:
```bash
sudo setsebool -P authlogin_yubikey 1
```

Or add SELinux policy module if boolean not available on your version.

## Per-User vs System-Wide authfile

| Approach | Path | When to use |
|----------|------|-------------|
| Per-user | `~/.config/Yubico/u2f_keys` | Personal workstation, user manages own key |
| System-wide | `/etc/u2f_mappings` | Multi-user, managed by admin |

For sudo/login: use system-wide (`authfile=/etc/u2f_mappings`). Per-user file may not be readable by PAM running as root unless `openasuser` option set.

With `openasuser`:
```
auth required pam_u2f.so openasuser cue
```
PAM reads `~/.config/Yubico/u2f_keys` as target user.
