# Feature Management Reference

ykman = primary CLI for all YubiKey interface management.
Read when: managing FIDO2, OTP slots, OATH/TOTP, OpenPGP, HSMAuth, or enabling/disabling interfaces.

Docs: https://developers.yubico.com/yubikey-manager/
Source: https://github.com/Yubico/yubikey-manager

## ykman Basics

```bash
ykman info                     # device info: serial, firmware, form factor, interfaces
ykman list                     # list all connected YubiKeys with serial numbers
ykman --device SERIAL <cmd>    # target specific key when multiple connected
ykman config usb --list        # list USB interface states
ykman config nfc --list        # list NFC interface states
```

### Install

```bash
pip install yubikey-manager         # universal (any distro)
sudo apt install yubikey-manager    # Debian/Ubuntu
sudo dnf install yubikey-manager    # Fedora/RHEL
sudo pacman -S yubikey-manager      # Arch
```

## Interface Management

Enable/disable YubiKey application interfaces per transport (USB/NFC). Changes take effect on reconnect.

```bash
# Disable OTP on USB (stops accidental OTP keypress)
ykman config usb --disable OTP

# Enable FIDO2 on NFC
ykman config nfc --enable FIDO2

# Enable everything on USB
ykman config usb --enable-all

# See current state
ykman config usb --list
ykman config nfc --list
```

Interface names: `OTP`, `FIDO`, `CCID`

`CCID` covers: PIV + OpenPGP + OATH + HSMAuth (all smart card interfaces).

## Firmware Feature Availability

Firmware is not upgradeable on YubiKey 5.

```bash
ykman info  # shows firmware version
```

| Feature | Minimum firmware |
|---------|----------------|
| FIDO2 | 5.0 |
| FIDO2 Resident Keys (discoverable) | 5.1 |
| Ed25519 in OpenPGP | 5.2.3 |
| HSMAuth | 5.4.3 |
| AES-192 PIV management key | 5.7 |
| FIDO2 Enterprise Attestation | 5.4 |

## FIDO2 Management

FIDO2 = WebAuthn / hardware passkey interface. No pcscd needed.

```bash
ykman fido info                          # PIN state, resident key count, FIDO2 version
ykman fido set-pin                       # set PIN (first time, no current PIN needed)
ykman fido change-pin                    # change existing PIN
ykman fido reset                         # factory reset FIDO2 (deletes ALL resident keys)
ykman fido credentials list              # list resident credentials (discoverable)
ykman fido credentials delete <id>       # delete specific resident credential
```

### Set/Change FIDO2 PIN

```bash
ykman fido set-pin
# Prompts for new PIN

ykman fido change-pin
# Prompts for old PIN, then new PIN
```

FIDO2 PIN: minimum 4 chars, max 63 chars. Unicode supported.

### Resident Credentials (Passkeys stored on key)

```bash
# List stored passkeys
ykman fido credentials list

# Delete one
ykman fido credentials delete <credential-id>
```

Register resident credential via pamu2fcfg:
```bash
pamu2fcfg -r -u $USER > ~/.config/Yubico/u2f_keys
```

### Security Policies

```bash
# Require PIN minimum length
ykman fido config set-min-pin-length 8

# Always require UV (user verification) regardless of what RP requests
ykman fido config set-always-uv true

# Enable enterprise attestation (firmware 5.4+)
ykman fido config enable-enterprise-attestation
```

### FIDO2 Reset

**Destroys all FIDO2 credentials registered on this key (website logins, passkeys, pam-u2f registrations). Irreversible.**

Must be done within 5 seconds of inserting key:

```bash
ykman fido reset
```

## OTP Management

Two OTP slots: slot 1 = short press, slot 2 = long press (hold 1.5+ seconds).

```bash
ykman otp info                  # show slot 1 and slot 2 config
ykman otp delete 1              # clear slot 1
ykman otp delete 2              # clear slot 2
```

### Yubico OTP (default on slot 1)

Cloud-validated one-time passwords. Works with YubiCloud and custom validation servers.

```bash
ykman otp yubiotp 1             # re-program slot 1 (new key ID, secret)
ykman otp yubiotp 2             # program slot 2
```

Options: `--upload` to register with YubiCloud automatically.

### Static Password (Keyboard Output)

YubiKey types static string on press. Good for long, complex passwords without typing.

```bash
ykman otp static 2                           # set slot 2 to random static password
ykman otp static 2 --generate               # same, explicit
ykman otp static 2 --password "MyS3cret"   # set specific password
ykman otp static 2 --keyboard-layout US     # specify layout (important for non-US)
```

Keyboard layouts: US, UK, DE, FR, IT, SE, and others.

### Challenge-Response (HMAC-SHA1)

Used by KeePassXC, KeePass, and other local tools. Slot 2 common.

```bash
ykman otp chalresp 2                  # configure with random secret
ykman otp chalresp 2 --generate       # same
ykman otp chalresp 2 --touch-button   # require touch for each challenge
```

## OATH Applet (TOTP/HOTP — Recommended over OTP slot)

Full TOTP/HOTP management via CCID. Stores up to 32 accounts (standard) or more (firmware 5.7+).
**Requires pcscd.**

```bash
ykman oath info                    # applet info, account count, password state
ykman oath accounts list           # list all stored accounts
ykman oath accounts code           # generate codes for all accounts
ykman oath accounts code example   # generate code for accounts matching "example"
```

### Add TOTP Account

```bash
# Basic TOTP
ykman oath accounts add -t example.com user@example.com

# HOTP
ykman oath accounts add -H example.com user@example.com

# From otpauth:// URI (from QR code — decode QR first, or use camera app)
ykman oath accounts uri "otpauth://totp/Example:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Example"

# Require touch before generating code
ykman oath accounts add -t -T example.com user@example.com

# 8-digit code (default 6)
ykman oath accounts add -t -d 8 example.com user@example.com
```

`-t` = TOTP, `-H` = HOTP, `-T` = require touch, `-d N` = digits (6 or 8)

### Generate Codes

```bash
ykman oath accounts code               # all accounts
ykman oath accounts code github        # filter by name
ykman oath accounts code -s            # show remaining seconds
```

### Delete Account

```bash
ykman oath accounts delete example.com
```

### Password-Protect OATH Applet

Prevents reading codes without knowing password.

```bash
ykman oath access change              # set new OATH password
ykman oath access change -c           # clear password
```

### OATH Reset

**Deletes all OATH accounts stored on key. Irreversible.**

```bash
ykman oath reset
```

## OpenPGP Management

YubiKey acts as GnuPG smart card. Three subkey slots: Sign, Encrypt, Authenticate.
**Requires pcscd.**

```bash
ykman openpgp info                    # card info, key status, algorithms, PIN retries
```

### Default PINs — Change Immediately

| PIN | Default | Use |
|-----|---------|-----|
| User PIN | `123456` | Required for sign/auth/encrypt operations |
| Admin PIN | `12345678` | Required for card administration |
| Reset Code | (none) | Optional; resets User PIN without Admin |

### Change PINs via gpg

```bash
gpg --card-edit
> passwd
# Select: 1 = change PIN, 2 = unblock PIN, 3 = change Admin PIN
> quit
```

Or via ykman:
```bash
ykman openpgp access change-pin
ykman openpgp access change-admin-pin
ykman openpgp access change-reset-code
```

### Set PIN Retry Counters

```bash
ykman openpgp set-pin-retries 3 3 3   # user retries, reset retries, admin retries
```

### Generate GPG Keys on YubiKey

Keys generated on-device never leave the hardware.

```bash
gpg --card-edit
> admin
> generate
# Follow prompts: key type, expiry, name, email
> quit
```

### Move Existing GPG Subkeys to YubiKey

**Export backup first. `keytocard` is one-way — key stub replaces local key.**

```bash
# Backup first
gpg --export-secret-keys --armor <KEYID> > backup_$(date +%Y%m%d).asc

# Move keys to card
gpg --edit-key <KEYID>
> key 1         # select subkey 1 (Signing)
> keytocard     # move to Sign slot
> key 1         # deselect
> key 2         # select subkey 2 (Encrypt)
> keytocard     # move to Encrypt slot
> key 2
> key 3         # select subkey 3 (Authenticate)
> keytocard     # move to Auth slot
> save
```

After `keytocard`, private key replaced by stub on local machine. Key lives on YubiKey only.

### Change Key Algorithm

```bash
gpg --card-edit
> admin
> key-attr
# Options: RSA 2048, RSA 4096, CV25519 (ed25519/x25519), nistp256
```

### SSH via GPG Authentication Subkey

```bash
# ~/.gnupg/gpg-agent.conf
enable-ssh-support

# Add to shell config (~/.bashrc, ~/.zshrc, ~/.config/fish/config.fish)
export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
gpgconf --launch gpg-agent

# List SSH keys from GPG agent
ssh-add -L

# Use public key for authorized_keys
ssh-add -L >> ~/.ssh/authorized_keys  # on remote host
```

gpg-agent handles PIN prompts on use.

### OpenPGP Reset

**Destroys all GPG keys on card. Irreversible without backup.**

```bash
ykman openpgp reset
```

Or via gpg:
```bash
gpg --card-edit
> admin
> factory-reset
```

### OpenPGP Touch Policies

```bash
ykman openpgp set-touch sig on       # require touch for signing
ykman openpgp set-touch enc on       # require touch for encryption
ykman openpgp set-touch aut on       # require touch for authentication
ykman openpgp set-touch sig fixed    # require touch, permanent (needs admin pin to undo)
```

## HSMAuth (firmware 5.4.3+)

Hardware-backed authentication credentials. Separate from FIDO2 and PIV. Used in enterprise contexts.

```bash
ykman hsmauth info
ykman hsmauth credentials list
ykman hsmauth credentials add -m AES128 myapp        # add AES-128 credential
ykman hsmauth credentials add -m AES256 myapp        # add AES-256 credential
ykman hsmauth credentials calculate myapp --context <hexcontext>
ykman hsmauth credentials delete myapp
ykman hsmauth reset                                  # reset all HSMAuth credentials
```

Management key required for some operations:
```bash
ykman hsmauth credentials add -m AES128 myapp -M <mgmt-key>
```

## Multi-YubiKey Operations

```bash
ykman list                             # list all with serial numbers
ykman --device 12345678 info           # target by serial
ykman --device 12345678 fido info
ykman --device 12345678 oath accounts code
```

## Legacy: YubiKey Personalization Tool (ykpers)

Older tool, use ykman instead for new deployments. Still available for advanced OTP slot configuration.

Source: https://github.com/Yubico/yubikey-personalization

```bash
sudo apt install yubikey-personalization
ykpers --help
```

## ykman Completion (Shell)

```bash
# bash
eval "$(_YKMAN_COMPLETE=source_bash ykman)"

# zsh
eval "$(_YKMAN_COMPLETE=source_zsh ykman)"

# fish
eval (env _YKMAN_COMPLETE=source_fish ykman)
```

## FIPS Mode (YubiKey FIPS Series)

YubiKey FIPS = hardware-validated version of YubiKey 5 series. FIPS 140-2/140-3 certified.

Check if key is FIPS:
```bash
ykman info  # shows "FIPS Approved Mode" status
```

### FIPS-Disabled Operations

These operations are blocked in FIPS mode (per FIPS 4 Series Technical Manual):
- ECDSA with SHA-1
- EC key with curve secp256k1
- RSA PKCS#1 decrypt (no padding)
- RSA PKCS#1 SHA-1 signing
- RSA PSS SHA-1 signing

Use SHA-256 or higher. Use secp256r1/secp384r1 (not secp256k1).

### FIPS OTP — Access Code Requirement

In FIPS mode, OTP slots must have an access code set. Modification without code rejected.

```bash
ykman otp --access-code <6-byte-hex> yubiotp 1   # program with access code
ykman otp --access-code <6-byte-hex> delete 1     # delete with code
ykman otp --access-code <6-byte-hex> settings 1   # apply access code to existing
```

Blank (disable) with access code:
```bash
ykman otp --access-code <code> chalresp 1 000000000000000000000000000000
```

### FIPS OATH — Authentication Key

OATH in FIPS mode requires an authentication key (password) set. Default = not set, must be configured.

```bash
ykman oath set-password -n <authentication-key>
ykman oath info   # verify OATH FIPS status shows "Enabled"
```

### FIPS Sub-Module Status

```bash
ykman otp info    # shows OTP FIPS status
ykman oath info   # shows OATH FIPS status
ykman fido info   # shows FIDO FIPS status
ykman openpgp info
ykman piv info
```

### FIPS Credential Requirements

| Credential | FIPS Min Length | FIPS Max Length |
|-----------|-----------------|-----------------|
| OTP Access Code | 6 bytes | 6 bytes |
| OATH Auth Key | 14 bytes | 64 bytes |
| PIV Management Key | 3DES (24 bytes) | AES-256 (32 bytes) |
| PIV PIN | 6 chars | 8 chars |
| OpenPGP User PIN (PW1) | 6 chars | 127 chars |
| OpenPGP Admin PIN (PW3) | 8 chars | 127 chars |
| FIDO2 PIN | 6 chars | 32 chars |

### FIPS Attestation

YubiKey FIPS certs include X.509 extension OID `1.3.9.1.4.1.41482.4.10` indicating FIPS status.

```bash
# Attest PIV key and verify FIPS OID
yubico-piv-tool -s9a -aattest -ocert_attest.pem
openssl x509 -in cert_attest.pem -text | grep -A2 "1.3.9.1.4.1.41482"
```

## YubiHSM 2 (Separate Product — Hardware Security Module)

YubiHSM 2 is not a YubiKey — it's a nano-form-factor HSM for server use. Different tool: `yubihsm-shell`.
Source: https://github.com/Yubico/yubihsm2-sdk

### Linux Setup

```bash
# Install SDK (Debian/Ubuntu)
sudo apt install yubihsm2-shell libyubihsm-dev

# Or from Yubico release packages:
# https://developers.yubico.com/yubihsm-2/Releases/

# Start connector (required — acts as USB bridge over HTTP)
yubihsm-connector &

# Connect
yubihsm-shell --connector http://localhost:12345
```

### yubihsm-shell Commands

```bash
# Session
yubihsm> connect                            # connect to connector
yubihsm> session open 1 password            # open session (auth key 1, default pw)

# Key generation
yubihsm> generate asymmetric 0 0 mykey 1 sign-ecdsa ecp256
yubihsm> generate asymmetric 0 0 mykey 1 rsa-pkcs1-sha256 rsa2048

# List objects
yubihsm> list objects 0 any 0 0 any

# Sign
yubihsm> sign ecdsa 0 0x0064 ecp256 sha256 data.bin

# Export/backup
yubihsm> export wrapped 0 0x0016 wrap asymmetric 0x0064

# Session close
yubihsm> session close 0
yubihsm> disconnect
```

### PKCS#11 with YubiHSM 2

```bash
# /etc/yubihsm_pkcs11.conf
connector = http://127.0.0.1:12345

# Use with OpenSSL
openssl engine -t pkcs11
OPENSSL_CONF=/etc/openssl-yubihsm.cnf openssl req -new -key "pkcs11:..." -out req.csr

# Use with SSH (host key in HSM)
ssh-keygen -D /usr/lib/x86_64-linux-gnu/pkcs11/yubihsm_pkcs11.so
```

### Integration Guides (Linux)

All accessible at developers.yubico.com:
- OpenSSH certificates for host login
- OpenSC pkcs11-tool integration
- OpenSSL with libp11
- OpenSSL with engine_pkcs11

### Capabilities (Permissions Model)

YubiHSM 2 uses fine-grained capability flags per key:
- `sign-ecdsa` — ECDSA signing
- `decrypt-pkcs` — RSA PKCS#1 decrypt
- `export-wrapped` — export object under wrap key
- `exportable-under-wrap` — object can be wrapped for export
- `get-log-entries` — read tamper-evident audit log

Default auth key (ID 1, password "password") has full capabilities — change immediately in production.
