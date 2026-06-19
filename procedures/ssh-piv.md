# Procedure: SSH Authentication via PIV Certificate

**Goal:** SSH login using key stored in YubiKey PIV slot 9a (no software key file).
**Time:** ~15 min
**Requires:** pcscd running, yubico-piv-tool installed

---

## Prerequisites

```bash
# pcscd must be running
systemctl is-active pcscd || sudo systemctl enable --now pcscd

# yubico-piv-tool installed
yubico-piv-tool -averify-pin -P123456   # uses default PIN — should succeed if key connected

# Find libykcs11 (needed for SSH)
find /usr -name 'libykcs11.so*' 2>/dev/null
```

---

## Procedure

### 1 — Change default PIN and Management Key

```bash
# Change PIN (default: 123456)
yubico-piv-tool -achange-pin -P123456 -N <newpin>

# Change PUK (default: 12345678)
yubico-piv-tool -achange-puk -P12345678 -N <newpuk>

# Change management key (fw ≤5.4 uses 3DES — 48 hex chars)
# Generate random key:
KEY=$(openssl rand -hex 24)
echo "Save this key: $KEY"
yubico-piv-tool -aset-mgm-key -m 010203040506070801020304050607080102030405060708 -n $KEY

# fw 5.7+ can use AES-192:
yubico-piv-tool -aset-mgm-key --algorithm AES192 -m 010203040506070801020304050607080102030405060708 -n $KEY
```

### 2 — Generate key in slot 9a (Authentication)

```bash
# Generate on-device key (private key never leaves YubiKey)
yubico-piv-tool -agenerate -s9a -AECCP256 -k $KEY -o public.pem

# With touch policy (recommended — requires touch for every SSH auth):
yubico-piv-tool -agenerate -s9a -AECCP256 --touch-policy=always -k $KEY -o public.pem

# Available algorithms: ECCP256, ECCP384, RSA2048, RSA3072, RSA4096
```

### 3 — Create self-signed certificate (required by PIV spec)

```bash
# Subject can be anything — it's just metadata on the card
yubico-piv-tool -averify-pin -P<pin> -aselfsign -s9a \
  --subject "/CN=SSH Auth $(hostname)/" \
  -i public.pem -o cert.pem

yubico-piv-tool -aimport-certificate -s9a -i cert.pem -k $KEY
```

Or generate CSR and get it signed by a CA:
```bash
yubico-piv-tool -averify-pin -P<pin> -arequest -s9a \
  --subject "/CN=SSH Auth $(hostname)/" \
  -i public.pem -o csr.pem
# ... sign csr.pem with CA ...
yubico-piv-tool -aimport-certificate -s9a -i signed_cert.pem -k $KEY
```

### 4 — Extract SSH public key

```bash
# Using libykcs11 (Yubico's PKCS#11 module)
LIBYKCS11=$(find /usr -name 'libykcs11.so*' 2>/dev/null | head -1)
ssh-keygen -D $LIBYKCS11 -e

# Or using OpenSC:
ssh-keygen -D /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so -e
```

Output is the SSH public key — copy it to remote server.

### 5 — Copy public key to remote server

```bash
LIBYKCS11=$(find /usr -name 'libykcs11.so*' 2>/dev/null | head -1)
ssh-copy-id -f -i <(ssh-keygen -D $LIBYKCS11 -e) user@remote-host
```

### 6 — Configure SSH client

```bash
# ~/.ssh/config
Host remote-host
    PKCS11Provider /path/to/libykcs11.so
```

Or use at CLI level:
```bash
ssh -I $LIBYKCS11 user@remote-host
```

### 7 — Test

```bash
ssh -I $LIBYKCS11 user@remote-host
# Prompts for PIN, then touch if touch policy set
```

---

## Verify

```bash
# Check what keys are on card
LIBYKCS11=$(find /usr -name 'libykcs11.so*' 2>/dev/null | head -1)
ssh-keygen -D $LIBYKCS11

# Check cert on slot 9a
yubico-piv-tool -astatus
yubico-piv-tool -aread-cert -s9a | openssl x509 -text -noout
```

---

## Alternative: Using OpenSC

```bash
# List keys
pkcs11-tool --module /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so -l -O

# Extract SSH public key
ssh-keygen -D /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so -e

# p11tool (GnuTLS)
p11tool --list-tokens
p11tool --list-all-certs
```

---

## Key Slots Reference

| Slot | Name | PIN Required | Typical Use |
|------|------|-------------|------------|
| 9a | Authentication | Always | SSH, client auth |
| 9c | Digital Signature | Always + confirm | Code signing, email |
| 9d | Key Management | Once per session | TLS, encryption |
| 9e | Card Auth | Never | Physical access |

---

## Troubleshoot

| Symptom | Cause | Fix |
|---------|-------|-----|
| `No reader found` | pcscd not running | `sudo systemctl start pcscd` |
| `Failed to connect to reader` | GnuPG scdaemon conflict | `gpgconf --kill scdaemon` |
| `ssh-keygen -D` shows nothing | Wrong libykcs11 path | `find /usr -name 'libykcs11.so*'` |
| SSH asks for password anyway | PKCS11Provider not in config or wrong path | Verify path exists; use `-I flag` test |
| PIN locked | 3 wrong PINs | Unblock with PUK: `yubico-piv-tool -aunblock-pin -P<puk> -N <newpin>` |
| Touch required but not prompted | touch-policy=always set, terminal swallowed prompt | Ensure SSH_ASKPASS or pinentry configured |
