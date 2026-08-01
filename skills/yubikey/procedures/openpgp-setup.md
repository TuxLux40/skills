# Procedure: OpenPGP Key Setup on YubiKey

**Goal:** Store GPG subkeys on YubiKey card, use for signing/encryption/SSH.
**Time:** ~30 min
**Requires:** pcscd running, gnupg ≥2.1

**Two paths:**
- **A: Move existing key** — subkeys from existing GPG key onto card
- **B: Generate on card** — key never exists in software (no backup)

---

## Prerequisites

```bash
# pcscd running
systemctl is-active pcscd || sudo systemctl enable --now pcscd

# scdaemon can see card
gpg --card-status   # must show card info, not error

# If gpg --card-status fails: see openpgp-scdaemon.md
```

---

## Path A: Move Existing Subkeys to Card

### 1 — Backup first (CRITICAL)

`keytocard` is destructive — it deletes the local private key stub. If card is lost, key is gone.

```bash
# Export full key (encrypted by passphrase)
gpg --export-secret-keys --armor <KEYID> > key_backup.gpg.asc
# Store backup_key.gpg.asc somewhere safe (encrypted USB, password manager)
```

### 2 — Change card PINs (default: user=123456, admin=12345678)

```bash
gpg --card-edit
gpg/card> admin
gpg/card> passwd
# Option 1: Change PIN (user PIN, 6+ chars)
# Option 3: Change Admin PIN (8+ chars)
gpg/card> quit
```

### 3 — Move subkeys to card slots

```bash
gpg --edit-key <KEYID>

gpg> key 1          # select first subkey (Sign)
gpg> keytocard      # sends to card, slot 1 (Signature)

gpg> key 1          # deselect
gpg> key 2          # select second subkey (Encrypt)
gpg> keytocard      # slot 2 (Encryption)

gpg> key 2
gpg> key 3          # select auth subkey
gpg> keytocard      # slot 3 (Authentication)

gpg> save
```

After save, `gpg -K` shows `ssb>` (stub) instead of `ssb` — key is on card.

**GnuPG 2.4.3 bug:** private key backup retained unprotected after keytocard on versions 2.4.2–2.4.3. Diagnose:
```bash
gpg-card checkkeys
```

### 4 — Verify

```bash
gpg --card-status   # should show key fingerprints in all 3 slots
echo "test" | gpg --clearsign   # prompts for PIN + touch
```

---

## Path B: Generate Key Directly on Card

**Warning:** private key never leaves card. No backup possible. Card loss = key loss.

```bash
gpg --card-edit
gpg/card> admin
gpg/card> generate
# Follow prompts: key size, expiry, name, email, passphrase
gpg/card> quit
```

Generated key appears in keyring automatically. Export public key:
```bash
gpg --export --armor <KEYID> > pubkey.asc
```

---

## Configure Touch Policy (YubiKey 5+)

```bash
# Require touch for every sign/encrypt/auth operation
ykman openpgp keys set-touch sig on    # signing
ykman openpgp keys set-touch enc on    # encryption
ykman openpgp keys set-touch aut on    # authentication (SSH)

# Cached touch (once per 15 seconds)
ykman openpgp keys set-touch sig cached
```

---

## SSH via GPG Authentication Subkey

### 1 — Configure gpg-agent

```bash
# ~/.gnupg/gpg-agent.conf
enable-ssh-support
default-cache-ttl-ssh 600
```

Restart:
```bash
gpg-connect-agent reloadagent /bye
```

### 2 — Set SSH_AUTH_SOCK

```bash
# bash/zsh — add to shell rc
export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
export GPG_TTY=$(tty)
gpgconf --launch gpg-agent
```

```fish
# fish
set -x SSH_AUTH_SOCK (gpgconf --list-dirs agent-ssh-socket)
set -x GPG_TTY (tty)
```

### 3 — Get SSH public key

```bash
gpg --export-ssh-key <KEYID>
# Copy output to ~/.ssh/authorized_keys on remote
```

### 4 — Verify

```bash
ssh-add -L   # should show: ssh-rsa/ecdsa/ed25519 ... cardno:...
```

---

## Alternative: openpgp-card-tools (oct)

`oct` is a modern alternative to `gpg --card-edit` (Arch: `openpgp-card-tools`).

```bash
oct list                              # list connected cards
oct status                            # show card info
oct info                              # technical details

# Import existing key
oct admin --card XXXX:XXXXXXXX import <(gpg --export-secret-key <FINGERPRINT>)

# Export SSH public key
oct ssh --card XXXX:XXXXXXXX --key-only

# Change PINs
oct pin --card XXXX:XXXXXXXX

# Sign/decrypt
oct sign --card XXXX:XXXXXXXX detached file.txt
oct decrypt --card XXXX:XXXXXXXX message.pgp

# Attest key (YubiKey-specific)
oct attestation --card XXXX:XXXXXXXX
```

JSON output for scripting:
```bash
oct --output-format=json list
oct --output-format=json status
```

---

## Set Key Attributes (Algorithm)

```bash
gpg --card-edit
gpg/card> admin
gpg/card> key-attr
# Choose RSA/ECC, key size for each slot
```

Or via ykman:
```bash
ykman openpgp keys set-touch sig on     # touch policy only via ykman
```

---

## PIN Retry Counter

```bash
ykman openpgp access set-retries 5 5 5   # user, reset, admin
```

---

## Reset OpenPGP Applet (nuclear option)

```bash
ykman openpgp reset
# Deletes all keys, resets PINs to defaults (123456 / 12345678)
```

---

## Troubleshoot

| Symptom | Cause | Fix |
|---------|-------|-----|
| `gpg --card-status` fails | scdaemon conflict with pcscd | See openpgp-scdaemon.md |
| `keytocard` rejects key | Wrong key type for slot | Sign key → slot 1; Enc → slot 2; Auth → slot 3 |
| `ssb` not `ssb>` after save | Did not run `save` in gpg edit | Redo keytocard + save |
| SSH key not shown by `ssh-add -L` | `enable-ssh-support` not in gpg-agent.conf | Add it; `gpg-connect-agent reloadagent /bye` |
| Touch required but no prompt | pinentry not configured | Set `pinentry-program` in gpg-agent.conf |
| Card PIN locked | 3 wrong attempts | `gpg --card-edit` → admin → passwd → Unblock |
