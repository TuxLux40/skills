# YubiKey Linux: Reference Links

All links organized by category.
[H] = human reading / manual research
[A] = agent should fetch for updates and edge cases not documented here

## Official Yubico Developer Portal

All developers.yubico.com URLs are **ACCESSIBLE** to crawlers — fetch directly.

| URL | Purpose | Tags |
|-----|---------|------|
| https://developers.yubico.com/ | Main dev hub, all products | [H][A] |
| https://developers.yubico.com/pam-u2f/ | pam-u2f full docs, all module options | [H][A] |
| https://developers.yubico.com/libfido2 | libfido2 library, FIDO2 protocol details | [H][A] |
| https://developers.yubico.com/libfido2/Manuals/fido2-token.html | fido2-token CLI reference | [H][A] |
| https://developers.yubico.com/yubikey-manager/ | ykman CLI + GUI full reference | [H][A] |
| https://developers.yubico.com/PIV/ | PIV specification, slot details, workflows | [H][A] |
| https://developers.yubico.com/U2F/App_ID.html | U2F App ID specification | [H] |
| https://developers.yubico.com/SSH/ | SSH with YubiKey (all methods) | [H][A] |
| https://developers.yubico.com/PGP/ | OpenPGP on YubiKey full guide | [H][A] |
| https://developers.yubico.com/yubihsm-2/ | YubiHSM 2 docs hub | [H][A] |

## GitHub Source Repositories

All github.com URLs are **ACCESSIBLE** to crawlers — fetch directly.
For latest options, changelogs, issues, and edge cases not in docs.

| URL | Project | Tags |
|-----|---------|------|
| https://github.com/Yubico/pam-u2f | pam-u2f: source, issues, new options | [A] |
| https://github.com/Yubico/yubikey-manager | ykman: source, changelog, install scripts | [A] |
| https://github.com/Yubico/yubico-piv-tool | yubico-piv-tool: source, build, issues | [A] |
| https://github.com/Yubico/yubikey-personalization | ykpers (legacy OTP tool) | [H] |
| https://github.com/Yubico/libu2f-host | U2F host library | [H] |
| https://github.com/Yubico/libfido2 | libfido2 source | [A] |
| https://github.com/Yubico/yubihsm2-sdk | YubiHSM 2 SDK and connector | [A] |

## udev Rules — Canonical Upstream Versions

Always check these when rules seem outdated or new YubiKey models not recognized.

| URL | File | Tags |
|-----|------|------|
| https://github.com/Yubico/yubikey-personalization/blob/master/69-yubikey.rules | OTP/smart card udev | [A] |
| https://github.com/Yubico/libu2f-host/blob/master/70-u2f.rules | FIDO2/U2F udev | [A] |

Raw versions (for wget/curl):
```
https://raw.githubusercontent.com/Yubico/yubikey-personalization/master/69-yubikey.rules
https://raw.githubusercontent.com/Yubico/libu2f-host/master/70-u2f.rules
```

## Security Advisories

| URL | CVE | Summary |
|-----|-----|---------|
| https://access.redhat.com/security/cve/CVE-2020-24612 | CVE-2020-24612 | pam-u2f SELinux silent failure — may allow bypass on SELinux-enforcing systems |

## PAM Documentation

| URL | Notes | Tags | Crawler |
|-----|-------|------|---------|
| http://linux.kernel.org/pub/linux/libs/pam | Linux-PAM source + docs | [H] | **UNREACHABLE** — server timeout |
| http://www.kernel.org/pub/linux/libs/pam | Alternate PAM docs URL | [H] | **UNREACHABLE** — server timeout |
| https://listman.redhat.com/mailman/listinfo/pam-list | PAM mailing list archive | [H] | untested |

## Distribution-Specific Guides

| URL | Notes | Tags | Crawler |
|-----|-------|------|---------|
| https://wiki.archlinux.org/title/YubiKey | Arch wiki: comprehensive, kept up-to-date | [H][A] | **BLOCKED** — Anubis v1.25.0; use search MCP or local cached HTML in project dir |
| https://wiki.archlinux.org/title/GnuPG | Arch GnuPG wiki: scdaemon, pcscd, SSH via GPG | [H][A] | **BLOCKED** — Anubis v1.25.0 |
| https://wiki.archlinux.org/title/PKCS11 | PKCS#11 on Arch, smart card integration | [H] | **BLOCKED** — Anubis v1.25.0 |
| https://ubuntu.com/security/certifications/docs/u2f | Ubuntu official U2F guide | [H] | untested |

## Pre-Registration and Enterprise

| URL | Notes | Tags |
|-----|-------|------|
| https://www.yubico.com/works-with-yubikey/catalog/ | Works-with catalog (identity providers, apps) | [H] |

## GnuPG / OpenPGP References

| URL | Notes | Tags |
|-----|-------|------|
| https://www.gnupg.org/howtos/card-howto/en/smartcard-howto.html | Official GnuPG SmartCard HOWTO | [H][A] |
| https://wiki.archlinux.org/title/GnuPG | Arch GnuPG wiki: YubiKey config, pcscd, SSH via GPG, troubleshooting | [H][A] |
| https://gnupg.org/documentation/manuals.html | All official GnuPG manuals | [H] |
| https://wiki.gnupg.org/WKD | Web Key Directory documentation | [H] |

## How Agents Should Use These Links

### Crawler Accessibility Summary (tested 2026-06-19)

| Domain | Status | How to access |
|--------|--------|---------------|
| developers.yubico.com | **ACCESSIBLE** | Fetch directly |
| github.com | **ACCESSIBLE** | Fetch directly |
| access.redhat.com | **ACCESSIBLE** | Fetch directly |
| gnupg.org | **ACCESSIBLE** | Fetch directly |
| wiki.archlinux.org | **BLOCKED** (Anubis) | Use search MCP; local HTML files in project dir as fallback |
| linux.kernel.org | **UNREACHABLE** | Use search MCP for PAM docs; try kernel.org mirror |

### Agent Workflow

1. **For blocked/unreachable sites:** Use whatever search MCP is active in the session (Tavily, Brave, Perplexity, etc.). Don't assume a specific one — check what's available. Local HTML files in /home/oliver/Projects/yubikey-skill/ include ArchWiki copies.

2. **For accessible sites:** Fetch directly — use a fetch-capable MCP or `firecrawl-scrape` / `agent-browser` skill.

3. **Priority fetch targets for common gaps:**
   - Latest pam-u2f options → `https://developers.yubico.com/pam-u2f/`
   - Latest ykman commands → `https://developers.yubico.com/yubikey-manager/`
   - udev rule updates → fetch raw GitHub URLs above
   - SSH integration → `https://developers.yubico.com/SSH/`
   - OpenPGP guide → `https://developers.yubico.com/PGP/`
   - GnuPG smartcard → `https://www.gnupg.org/howtos/card-howto/en/smartcard-howto.html`
   - YubiHSM 2 → `https://developers.yubico.com/yubihsm-2/`

## Useful Search Queries

```
pam-u2f Linux sudo 2FA site:developers.yubico.com
YubiKey FIDO2 udev rules Linux plugdev
yubico-piv-tool SSH PKCS11 libykcs11
ykman OATH TOTP accounts Linux
YubiKey OpenPGP GnuPG SSH agent Linux scdaemon
YubiKey screen lock KDE GNOME PAM
YubiKey pcscd conflict scdaemon disable-ccid
YubiKey SELinux pam-u2f RHEL Fedora
YubiKey 5 firmware features comparison
GnuPG YubiKey OpenSC multi-applet conflict
polkit pcscd remote SSH card access
```
