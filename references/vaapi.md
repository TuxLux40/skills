# VA-API & Browser Hardware Acceleration Reference

## VA-API Driver Matrix

| GPU | Driver Package | Notes |
|-----|---------------|-------|
| Intel Broadwell+ (5th gen, 2014+) | `intel-media-driver` (iHD) | Recommended for modern Intel |
| Intel Haswell and older (4th gen, 2013-) | `libva-intel-driver` (i965) | Legacy only; iHD breaks on old GPUs |
| AMD (all modern) | `libva-mesa-driver` | Included in mesa |
| NVIDIA (open driver) | `libva-nvidia-driver` | Experimental; proprietary path = NVDEC |

**Critical**: Using `intel-media-driver` on Haswell or older causes silent failures. Detect with:
```bash
lspci | grep VGA  # look for Intel HD 4xxx or older = Haswell/legacy
```

## Verify VA-API
```bash
vainfo          # lists supported profiles
vainfo 2>&1 | grep -i error  # check for failures
```

Expected output on working Intel iHD:
```
libva info: VA-API version 1.x.x
Trying display: drm
libva info: Found init function __vaDriverInit_1_x
vainfo: VA-API version: 1.x (libva 2.x.x)
vainfo: Driver version: Intel iHD driver for Intel(R) Gen Graphics - ...
vainfo: Supported profile and entrypoints
      VAProfileH264Main               :   VAEntrypointVLD
      ...
```

## VA-API Install by Distro

### Arch
```bash
# Intel modern (Broadwell+)
sudo pacman -S intel-media-driver libva-utils

# Intel legacy (Haswell-)
sudo pacman -S libva-intel-driver libva-utils

# AMD
sudo pacman -S libva-mesa-driver libva-utils
```

### Debian/Ubuntu
```bash
# Intel modern
sudo apt install intel-media-va-driver vainfo

# Intel legacy
sudo apt install i965-va-driver vainfo

# AMD
sudo apt install mesa-va-drivers vainfo
```

### Fedora
```bash
# Intel modern
sudo dnf install intel-media-driver libva-utils

# Intel legacy
sudo dnf install libva-intel-driver libva-utils

# AMD (in mesa)
sudo dnf install mesa-va-drivers libva-utils
```

## LIBVA_DRIVER_NAME Override

Force a specific driver if auto-detection fails:
```bash
# Force iHD (Intel modern)
export LIBVA_DRIVER_NAME=iHD

# Force i965 (Intel legacy)
export LIBVA_DRIVER_NAME=i965

# Force radeonsi (AMD)
export LIBVA_DRIVER_NAME=radeonsi
```

Add to `~/.profile` or `/etc/environment` to persist.

---

## Browser Hardware Acceleration (Chromium-based, Wayland only)

**WARNING**: `--ozone-platform=wayland` BREAKS browsers on X11. Only apply if session is Wayland.
Detect: `echo $XDG_SESSION_TYPE` must return `wayland`.

### Flags (Chromium 143+ — works without flags for most scenarios)
```
--ozone-platform=wayland
--enable-features=VaapiVideoDecodeLinuxGL,VaapiVideoEncoder,WaylandWindowDecorations
```

### Config file locations (write flags here, one per line)
```
~/.config/brave-flags.conf
~/.config/chromium-flags.conf
~/.config/google-chrome-flags.conf
~/.config/microsoft-edge-flags.conf
```

### Verify in browser
Navigate to `chrome://media-internals` → play a video → look for `VDAVideoDecoder` or `VaapiVideoDecoder` in decoder field.

Or: `chrome://gpu` → look for "Video Decode: Hardware accelerated"

### Firefox (Wayland)
Firefox uses VA-API natively on Wayland since Firefox 96. Set in `about:config`:
- `media.ffmpeg.vaapi.enabled` = `true`
- `media.hardware-video-decoding.force-enabled` = `true` (if needed)

Or set env var: `MOZ_ENABLE_WAYLAND=1` (usually auto-detected)
