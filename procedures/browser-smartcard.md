# Procedure: Browser PKCS#11 / Smart Card Integration

**Goal:** Firefox/Chromium use YubiKey PIV certs for client TLS authentication.
**Time:** ~10 min
**Requires:** opensc installed, pcscd running

---

## Prerequisites

```bash
sudo apt install opensc pcsclite pcsc-tools  # Debian/Ubuntu
sudo pacman -S opensc pcsclite pcsc-tools    # Arch
sudo dnf install opensc pcsc-lite pcsc-tools # Fedora

# Verify card readable
pcsc_scan   # plug in YubiKey — should show ATR + card info
```

---

## Firefox

### Add PKCS#11 Module

1. Open Firefox → Preferences → Privacy & Security
2. Scroll to "Certificates" → click "Security Devices"
3. Click "Load"
4. Module Name: `YubiKey PKCS11` (any label)
5. Module filename:
   - Linux: `/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so`
   - Or Yubico's module: `/usr/lib/x86_64-linux-gnu/libykcs11.so`
   - Arch: `/usr/lib/pkcs11/opensc-pkcs11.so`
6. Click OK

Find the right path:
```bash
find /usr -name 'opensc-pkcs11.so' 2>/dev/null
find /usr -name 'libykcs11.so' 2>/dev/null
```

### Verify

Navigate to a site requiring client cert auth — Firefox should prompt to select certificate from YubiKey.

---

## Chromium / Chrome

Chromium uses NSS (Network Security Services) database, not browser preferences UI.

```bash
# Check existing modules
modutil -list -dbdir $HOME/.pki/nssdb/

# Add OpenSC PKCS#11 module
modutil -dbdir sql:$HOME/.pki/nssdb/ \
  -add "YubiKey PKCS11" \
  -libfile /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so

# Or Yubico's libykcs11:
modutil -dbdir sql:$HOME/.pki/nssdb/ \
  -add "YubiKey PKCS11" \
  -libfile $(find /usr -name 'libykcs11.so' 2>/dev/null | head -1)

# Verify added
modutil -list -dbdir $HOME/.pki/nssdb/
```

Restart Chrome/Chromium after adding module.

---

## p11-kit (System-Wide Module Loading)

p11-kit allows loading PKCS#11 modules system-wide. Apps that support p11-kit pick them up automatically.

```bash
# User-level config
mkdir -p ~/.config/pkcs11/modules
cat > ~/.config/pkcs11/modules/yubikey.module << 'EOF'
module: /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so
EOF

# System-level (all users)
sudo tee /etc/pkcs11/modules/yubikey.module << 'EOF'
module: /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so
EOF

# List tokens via p11tool (GnuTLS)
p11tool --list-tokens

# List certs
p11tool --list-all-certs

# List keys
p11tool --list-all-privkeys
```

---

## Diagnostics

```bash
# Scan readers and cards (pcsc-tools)
pcsc_scan
# Shows: reader names, ATR (card identifier), card events

# List objects on card via pkcs11-tool
pkcs11-tool --module /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so -O

# Login and list objects
pkcs11-tool --module /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so -l -O

# Test signing
pkcs11-tool --module /usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so \
  --sign --slot 0 --id 01 -m SHA256-RSA-PKCS \
  -i /dev/urandom --output /dev/null
```

---

## opensc.conf — Key Settings

```
# /etc/opensc.conf
app default {
    enable_pinpad = false;   # disable if no PIN pad on reader
}
```

---

## Troubleshoot

| Symptom | Cause | Fix |
|---------|-------|-----|
| Module loads but no certs | No certs in PIV slots | Run `yubico-piv-tool -astatus`; import cert |
| Firefox doesn't prompt for cert | Module not loaded or wrong path | Re-add via Security Devices with correct .so path |
| `LIBUSB_ERROR_BUSY` | GnuPG scdaemon has exclusive USB access | `gpgconf --kill scdaemon`; use pcscd mode in scdaemon.conf |
| `pcsc_scan` shows no reader | pcscd not running | `sudo systemctl start pcscd` |
| Chrome ignores NSS module | Module added while Chrome running | Restart Chrome |
| Cert appears but auth fails | Cert subject doesn't match TLS server expectation | Check cert CN/SAN vs server's client cert requirements |
