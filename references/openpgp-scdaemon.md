# OpenPGP / scdaemon Advanced Reference

Deep config for GnuPG smart card daemon (scdaemon), YubiKey multi-applet fixes, polkit for remote access.
Read when: scdaemon not finding card, pcscd conflict, SSH/remote access, OpenSC conflict with OpenPGP.

Sources: GnuPG ArchWiki, gnupg.pdf, GnuPG HOWTOs

Official smartcard HOWTO: https://www.gnupg.org/howtos/card-howto/en/smartcard-howto.html
ArchWiki GnuPG: https://wiki.archlinux.org/title/GnuPG

## scdaemon Configuration

`~/.gnupg/scdaemon.conf` controls how GnuPG talks to smart cards.

### GnuPG-only (direct USB, no pcscd)

```
reader-port 32768    # First USB reader (default)
```

Requires `libusb-compat`. Faster but exclusive — no sharing with other apps.

### GnuPG + pcscd (shared access)

Required when: OpenSC or other apps also use the card; YubiKey OpenPGP + PIV both needed.

**GnuPG ≤2.2.27 / 2.3.x:**
```
pcsc-driver /usr/lib/libpcsclite.so
card-timeout 5
disable-ccid
```

**GnuPG 2.2.28+ / 2.4+ (shared-access mode):**
```
pcsc-driver /usr/lib/libpcsclite.so
pcsc-shared
disable-ccid
```

Note: `pcsc-shared` described as "somewhat dangerous" due to card state caching. Use if exclusive access not possible.

**GnuPG 2.4+ critical:** Must set `disable-ccid` to use pcscd — behavior changed from earlier versions.

pcsclite library path varies:
- Arch: `/usr/lib/libpcsclite.so`
- Debian/Ubuntu: `/usr/lib/x86_64-linux-gnu/libpcsclite.so.1`
- Fedora: `/usr/lib64/libpcsclite.so.1`

Find it:
```bash
find /usr -name 'libpcsclite.so*' 2>/dev/null
```

### Restart scdaemon after config change

```bash
gpg-connect-agent "scd killscd" /bye
gpg-connect-agent /bye
```

Or kill and let it restart:
```bash
gpgconf --kill scdaemon
```

## YubiKey Multi-Applet Fix (OpenSC Conflict)

Problem: OpenSC PKCS#11 module switches YubiKey from OpenPGP to PIV applet, breaking scdaemon.
Symptom: `gpg --card-status` shows wrong card or fails after any PKCS#11 operation.

**Find YubiKey ATR:**
```bash
opensc-tool --atr
```

**Configure `/etc/opensc.conf` to force OpenPGP applet:**
```
app default {
    card_atr 3b:8c:80:01:59:75:62:69:6b:65:79:4e:45:4f:72:33:58 {
        name = "YubiKey NEO";
        driver = "openpgp";
    }
}
```

Replace the ATR value with output from `opensc-tool --atr`.

**Verify fix:**
```bash
pkcs11-tool -O --login
# Should select OpenPGP applet
```

## udev Rules for scard Group

Alternative to plugdev for GnuPG-specific access:

```bash
# /etc/udev/rules.d/71-gnupg-ccid.rules
ACTION=="add", SUBSYSTEM=="usb", ENV{ID_VENDOR_ID}=="1050", ENV{ID_MODEL_ID}=="0116|0111", MODE="660", GROUP="scard"
```

Create group and add user:
```bash
sudo groupadd scard
sudo usermod -aG scard $USER
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Model IDs from `lsusb`. Common YubiKey 5 models: `0407`, `0410`, `0111`, `0116`.

## SSH via GPG Authentication Key

Full SSH setup via GnuPG agent.

### Configure gpg-agent for SSH

```bash
# ~/.gnupg/gpg-agent.conf
enable-ssh-support
default-cache-ttl-ssh 600
max-cache-ttl-ssh 7200
```

### Export GPG Auth Key as SSH Public Key (GnuPG 2.1+)

```bash
gpg --export-ssh-key <KEY-ID-OR-EMAIL>
# or: fingerprint of the auth subkey
```

Add output to `~/.ssh/authorized_keys` on remote server.

### Set SSH_AUTH_SOCK in Shell

```bash
# ~/.bashrc / ~/.zshrc
export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
gpgconf --launch gpg-agent

# fish: ~/.config/fish/config.fish
set -x SSH_AUTH_SOCK (gpgconf --list-dirs agent-ssh-socket)
```

### Verify SSH Key Visible

```bash
ssh-add -L
# Should show: ssh-rsa/ecdsa/ed25519 ... cardno:000XXXXXXX
```

### Set GPG_TTY for PIN Entry

Required for pinentry-curses (terminal-based PIN dialog):
```bash
export GPG_TTY=$(tty)
```

Add to shell rc file.

### SSH with Key Stub — "Unusable public key" Error

If ssh returns "Unusable public key" add `!` suffix to keygrip:
```bash
gpg --edit-key <KEY-ID>
> toggle
> key <N>   # select auth subkey
> keytocard
```

Or use `gpg --expert --edit-key` to add an authentication-capable key.

## polkit Rules for Remote SSH / WSL Access

Problem: pcscd refuses card access when connecting via SSH or WSL (local-only polkit policy).

Symptom:
```
gpg: selecting card failed: No such device
gpg: OpenPGP card not available: No such device
```

Fix — create polkit rule:

```
# /etc/polkit-1/rules.d/99-pcscd.rules
polkit.addRule(function(action, subject) {
    if (action.id == "org.debian.pcsc-lite.access_card" &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
polkit.addRule(function(action, subject) {
    if (action.id == "org.debian.pcsc-lite.access_pcsc" &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
```

Replace `"wheel"` with your sudo group (`wheel` on Fedora/Arch, `sudo` on Debian/Ubuntu).

```bash
sudo systemctl restart polkit.service
```

## pcscd Socket vs Service Activation

Two modes — socket activation preferred (starts on demand):

```bash
# Socket activation (preferred)
sudo systemctl enable --now pcscd.socket

# Direct service
sudo systemctl enable --now pcscd.service
```

## gpg-agent Config: PIN Caching

```
# ~/.gnupg/gpg-agent.conf
default-cache-ttl 600         # cache PIN for 10 min (for signing ops)
max-cache-ttl 7200            # max 2 hours
default-cache-ttl-ssh 600     # SSH key cache
pinentry-program /usr/bin/pinentry-qt   # KDE
# pinentry-program /usr/bin/pinentry-gnome3  # GNOME
# pinentry-program /usr/bin/pinentry-curses  # terminal
```

Restart agent after change:
```bash
gpg-connect-agent reloadagent /bye
```

## Security Warning: GnuPG 2.4.3 Key Backup Bug

Affected versions: GnuPG 2.4.3, 2.4.2, 2.2.42

When moving keys to card via `gpg --edit-card`, private key backup retained in clear (not protected by passphrase).

Check if affected:
```bash
gpg-card checkkeys
```

Fix: delete lingering private key material after `keytocard` if on affected version.

Check your version:
```bash
gpg --version
```

## gpg-card (GnuPG 2.3+ Modern Interface)

Newer alternative to `gpg --card-edit`:

```bash
gpg-card             # interactive card management
gpg-card info        # show card status
gpg-card list        # list keys on card
gpg-card passwd      # change PINs
```

## Web Key Directory (WKD) — Publish GPG Public Key

WKD lets email clients auto-fetch your public key from your domain via HTTPS.

```bash
# Get the WKD hash for your email
gpg-wks-client --print-wkd-hash user@example.com

# Get the WKD URL
gpg-wks-client --print-wkd-url user@example.com

# Look up someone else's key
gpg --locate-external-keys user@example.com
```

Hosting: serve key at `https://example.com/.well-known/openpgpkey/hu/<hash>?l=<localpart>`

Or use subdomain method: `https://openpgpkey.example.com/.well-known/openpgpkey/example.com/hu/<hash>`

GnuPG WKD support since v2.1.12; enabled by default since v2.1.23.

Reference: https://wiki.gnupg.org/WKD

## CCID Architecture (Why Two Drivers Exist)

CCID (Chip Card Interface Device) = USB protocol for smart card readers. Defines 14 USB messages between host and reader. YubiKey is simultaneously a CCID reader AND the card.

Two competing Linux implementations:
- **libccid / pcsclite** — userspace CCID driver; apps access via pcscd daemon (PC/SC standard)
- **GnuPG internal CCID** — GnuPG's own direct USB driver; no daemon needed but exclusive access

Both work, but they fight over the same USB device. Must pick one:
- Using **only GnuPG**: set `reader-port 32768` in scdaemon.conf; don't run pcscd
- Using **pcscd for everything** (PIV + OpenSC + GnuPG): set `disable-ccid` in scdaemon.conf; GnuPG defers to pcscd

Key package: `ccid` (Arch/Debian) or `ccid` rpm — provides the libccid driver that pcscd loads.

## Key Config Files Summary

| File | Purpose |
|------|---------|
| `~/.gnupg/gpg-agent.conf` | Agent settings: SSH support, PIN cache, pinentry |
| `~/.gnupg/scdaemon.conf` | Smart card daemon: driver, pcscd mode |
| `/etc/opensc.conf` | Fix multi-applet conflict (force OpenPGP applet) |
| `/etc/polkit-1/rules.d/99-pcscd.rules` | Allow remote SSH/WSL pcscd access |
| `/etc/udev/rules.d/71-gnupg-ccid.rules` | udev permissions for scard group |
