# PIV Management Reference

PIV = Personal Identity Verification. Smart card interface for X.509 certs, SSH via cert, email signing.
Read when: generating/importing keys, managing certs, SSH via PIV, PIN management.

Requires: `pcscd` running, `yubico-piv-tool` installed.

Source: https://github.com/Yubico/yubico-piv-tool
Docs: https://developers.yubico.com/PIV/

## Prerequisites

```bash
# Start pcscd
sudo systemctl enable --now pcscd

# Install tool
sudo apt install yubico-piv-tool   # Debian/Ubuntu
sudo dnf install yubico-piv-tool   # Fedora/RHEL
sudo pacman -S yubico-piv-tool     # Arch
```

## Default Credentials — Change Immediately

**New YubiKey ships with these defaults. Change before use.**

| Credential | Default | Max wrong attempts |
|-----------|---------|-------------------|
| PIN | `123456` | 3 → blocked (unblock with PUK) |
| PUK | `12345678` | 3 → YubiKey bricked (PIV gone) |
| Management Key (fw ≤5.4, 3DES) | `010203040506070801020304050607080102030405060708` | n/a |
| Management Key (fw 5.7+, AES-192) | `010203040506070801020304050607080102030405060708` | n/a |

PIN: 6–8 characters. PUK: 6–8 characters. Management key: hex, used for admin operations.

## Key Slots

| Slot | Name | Purpose | PIN required |
|------|------|---------|-------------|
| 9A | Authentication | Login, SSH | Yes |
| 9C | Digital Signing | Signing docs/code | Yes, always |
| 9D | Key Management | Encryption/decryption | Yes |
| 9E | Card Authentication | Physical access, badge | No (by default) |
| 9B | Management | PIV management operations | Management key |
| 82–95 | Retired | Historical key mgmt (up to 20 retired keys) | Yes |
| F9 | Attestation | Factory attestation cert (read-only) | — |

## Device Status

```bash
yubico-piv-tool -astatus    # slots, PIN/PUK retry counts, firmware
yubico-piv-tool -aversion   # tool + firmware version
ykman piv info              # alternate via ykman
```

## PIN / PUK / Management Key Operations

### Verify PIN

```bash
yubico-piv-tool -averify-pin -P123456
```

### Change PIN

```bash
yubico-piv-tool -achange-pin -P123456 -N<newpin>
```

### Change PUK

```bash
yubico-piv-tool -achange-puk -P12345678 -N<newpuk>
```

### Unblock PIN with PUK (when PIN is blocked)

```bash
yubico-piv-tool -aunblock-pin -P<puk> -N<newpin>
```

### Change Management Key

```bash
yubico-piv-tool -aset-mgm-key -k
# Prompts: current key, then new key (hex)
```

### Set PIN Retries

```bash
yubico-piv-tool -k -apin-retries --pin-retries=3 --puk-retries=3
```

### Factory Reset PIV Applet

**Irreversible. Destroys all PIV keys, certs, returns to defaults.**

```bash
yubico-piv-tool -areset
```

## Generate Key on Device

Key never leaves YubiKey. Safer than importing.

### ECC P-256 in Slot 9A (recommended)

```bash
yubico-piv-tool -agenerate -s9a -AECCP256 -k
```

Outputs public key to stdout.

### RSA 2048 in Slot 9C

```bash
yubico-piv-tool -agenerate -s9c -ARSA2048 -k
```

### Available Algorithms

- `RSA1024` (not recommended)
- `RSA2048`
- `ECCP256` (secp256r1, recommended)
- `ECCP384` (secp384r1)

### Touch and PIN Policies

```bash
# Require touch every time (slot 9a)
yubico-piv-tool -agenerate -s9a -AECCP256 --touch-policy=always -k

# Require PIN every operation
yubico-piv-tool -agenerate -s9a -AECCP256 --pin-policy=always -k
```

`--touch-policy`: `never` | `always` | `cached` (cached = once per 15s)
`--pin-policy`: `never` | `once` (per session) | `always`

## CSR → Import Signed Certificate

Step 1: Generate key (see above)

Step 2: Create CSR:
```bash
yubico-piv-tool -s9a -S'/CN=myuser/O=myorg/C=US/' -averify -arequest -P123456 > request.csr
```

Step 3: Sign CSR with CA (external; send `request.csr` to CA).

Step 4: Import signed cert:
```bash
yubico-piv-tool -s9a -aimport-certificate -icert.pem -k
```

## Import Existing Private Key

Key leaves HSM — less secure than on-device generation.

```bash
yubico-piv-tool -aimport-key -s9a --touch-policy=always -ikey.pem -k
```

PKCS12 import (key + cert together):
```bash
yubico-piv-tool -s9c -itest.pfx -KPKCS12 -aimport-key -aimport-cert -aset-chuid -k
```

## Self-Signed Certificate (for SSH/testing)

No CA needed. Not trusted by browsers/CAs.

```bash
# After key generation:
yubico-piv-tool -s9a -S'/CN=myuser/O=myorg/' -averify -aselfsign -P123456 | \
  yubico-piv-tool -s9a -aimport-certificate -k
```

## Read / Export / Delete Certificate

```bash
# Read (display)
yubico-piv-tool -aread-cert -s9a

# Export to PEM file
yubico-piv-tool -aread-cert -s9a -ocert.pem

# Delete cert (keep key)
yubico-piv-tool -adelete-certificate -s9a -k
```

## Move Key Between Slots

```bash
yubico-piv-tool -amove-key -s9a -S9c -k
# Moves key from 9A to 9C
```

## Large Certificate Compression

Max cert size: 2025 bytes (NEO) / 3049 bytes (YK4+). Compress if exceeds limit:

```bash
openssl x509 -in cert.pem -outform DER | gzip -9 > der.gz
yubico-piv-tool -s9c -ider.gz -KGZIP -aimport-cert -k
```

## SSH with PIV via PKCS#11

No need for ssh-agent — PKCS#11 module handles PIN prompts directly.

### List Available Keys

```bash
ssh-keygen -D /usr/lib/x86_64-linux-gnu/libykcs11.so
# On Fedora/RHEL:
ssh-keygen -D /usr/lib64/libykcs11.so
```

### Connect with YubiKey

```bash
ssh -I /usr/lib/x86_64-linux-gnu/libykcs11.so user@host
```

### Permanent `~/.ssh/config` Entry

```
Host myserver
    HostName myserver.example.com
    User alice
    PKCS11Provider /usr/lib/x86_64-linux-gnu/libykcs11.so
```

### Add Public Key to Server

```bash
ssh-keygen -D /usr/lib/x86_64-linux-gnu/libykcs11.so > yubikey_pub.pub
ssh-copy-id -f -i yubikey_pub.pub user@host
```

libykcs11.so path varies by distro:
- Debian/Ubuntu: `/usr/lib/x86_64-linux-gnu/libykcs11.so`
- Fedora: `/usr/lib64/libykcs11.so`
- Arch: `/usr/lib/libykcs11.so`

### Via OpenSC (alternative)

```bash
sudo apt install opensc

# List keys
pkcs15-tool --list-public-keys

# Add to ssh-agent
ssh-add -s /usr/lib/x86_64-linux-gnu/opensc-pkcs11.so
ssh-add -L  # verify
```

## Attestation

Prove key was generated on-device (not imported). Useful for enterprise policies.

```bash
# Attest slot 9A
yubico-piv-tool -s9a -aattest -ocert_attest.pem

# Get device CA cert
yubico-piv-tool -sf9 -aread-cert -oca_attest.pem

# Verify attestation
openssl verify -CAfile ca_attest.pem cert_attest.pem
```

## Slot 9E — No PIN

Card Authentication slot. Auth without PIN prompt — used for door access, badge readers, NFC.

```bash
yubico-piv-tool -agenerate -s9e -AECCP256 -k
yubico-piv-tool -s9e -averify -aselfsign -P123456 | \
  yubico-piv-tool -s9e -aimport-certificate -k
```

## List Smart Card Readers

```bash
yubico-piv-tool -alist-readers
```

## Object Read/Write

Raw PIV data object access (advanced):

```bash
yubico-piv-tool -aread-object --id=0x5fc105   # read CHUID
yubico-piv-tool -awrite-object --id=0x5fc105 -idata.bin -k
```

## Build from Source

Needed when distro package is too old.

```bash
# Dependencies
sudo apt install cmake libtool libssl-dev pkg-config check libpcsclite-dev gengetopt help2man zlib1g-dev

# Build
git clone https://github.com/Yubico/yubico-piv-tool.git
cd yubico-piv-tool
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig
```

Backend on GNU/Linux: `pcsc` (pcsclite). Other backends: `macscard` (macOS), `winscard` (Windows).

Optional cmake flags:
- `-DOPENSSL_STATIC_LINK=ON` — static OpenSSL
- `-DCMAKE_BUILD_TYPE=Release`

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `Failed to connect to yubikey` | pcscd not running | `systemctl start pcscd` |
| `PIN wrong` / lockout warning | Near 3-attempt limit | Stop immediately; use PUK: `aunblock-pin` |
| `No space on device` | Slot has cert | Delete first: `adelete-certificate -s9a -k` |
| `Verification of PIN failed` | Wrong PIN | Default is `123456`; check retry count in `astatus` |
| libykcs11.so not found for SSH | Wrong path | `find /usr -name 'libykcs11.so' 2>/dev/null` |
| `No smartcard found` via OpenSC | pcscd conflict or wrong reader | Try `pcsc_scan`; restart pcscd |
