# NVIDIA GPU Reference

Driver landscape (pick ONE):

| Driver | Package (Arch) | For |
|--------|---------------|-----|
| **nvidia** (proprietary, closed kernel modules) | `nvidia` / `nvidia-lts` / `nvidia-dkms` | Maxwell (900) → Ada; the classic choice |
| **nvidia-open** (proprietary userspace, open kernel modules) | `nvidia-open` / `nvidia-open-dkms` | Turing (1600/2000)+ — **NVIDIA's recommended default for Turing and newer** |
| **nouveau + NVK** (fully open) | `mesa` (NVK Vulkan in Mesa 24+) | Improving fast but still behind for gaming; OK for older cards, not competitive for new titles |

**Match rule that breaks constantly:** `nvidia-utils`, `lib32-nvidia-utils`, and the kernel module package must be the **exact same version**. Version skew after partial updates = `GLXBadContext`, Steam hanging at "Installing breakpad exception handler", games failing to launch.
```bash
pacman -Qs nvidia          # all versions must match
```

## Required setup

```bash
pacman -S nvidia-open-dkms nvidia-utils lib32-nvidia-utils   # Turing+
# DKMS variant rebuilds on kernel updates automatically (needs matching headers)

# KMS — required for Wayland, gamescope, and modern display stacks:
# kernel parameter:
nvidia-drm.modeset=1
# Fbdev (smoother VT/boot, driver 545+):
nvidia-drm.fbdev=1
```

**Early KMS / initramfs:** add `nvidia nvidia_modeset nvidia_uvm nvidia_drm` to `mkinitcpio.conf` MODULES and remove `kms` hook; regenerate initramfs. Without this: flicker/black screen between boot and display manager.

**`ERROR: module not found: 'nvidia'` from mkinitcpio:** modules expected but package missing for one of your installed kernels — install `nvidia` (or the `-dkms` variant + headers for every kernel).

**Secure Boot:** DKMS-built modules are unsigned → kernel refuses to load them → black screen/nouveau fallback. Either sign modules (sbctl/MOK) or disable Secure Boot. This is the #1 "driver installed but not loading" cause on dual-boot machines.

## Suspend/resume (games crash or corrupt after sleep)

```bash
# Preserve VRAM across suspend:
systemctl enable nvidia-suspend.service nvidia-resume.service nvidia-hibernate.service
# kernel parameter / modprobe option:
options nvidia NVreg_PreserveVideoMemoryAllocations=1
```
Without this, Vulkan apps (= every Proton game) lose device state on resume.

## Wayland / gamescope specifics

| Issue | Fix |
|-------|-----|
| Gamescope fails/black on NVIDIA | Needs `nvidia-drm.modeset=1`; driver 555+ with explicit sync is dramatically better — older drivers had chronic Xwayland flicker |
| Xwayland games flicker/tear (driver <555) | Upgrade driver; explicit-sync protocol landed in 555 + recent Xwayland |
| Flatpak gamescope window doesn't appear | `flatpak override --env=GBM_BACKENDS_PATH=/usr/lib/x86_64-linux-gnu/GL/nvidia-XXX-YY-ZZ/extra/gbm <app-id>` |
| HDR via gamescope | Known critical issues on NVIDIA — AMD recommended for HDR (see `display.md`) |
| Refresh rate capped at 120Hz on HDMI (driver 550+) | `nvidia-modeset.hdmi_deepcolor=0` kernel param (but deep color is required for HDR) |
| Display manager races driver at boot (fast NVMe systems) | Xorg starts before driver init — add ordering dependency on DRI device or enable early KMS |

## Performance / gaming env vars

```bash
__GL_SHADER_DISK_CACHE=1                       # shader cache on (default)
__GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1          # don't trim cache (default 1GB limit) — big shader-heavy games
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia %command%   # hybrid laptop dGPU offload
nvidia-smi                                     # utilization/VRAM/temp live
nvidia-settings                                # GUI; save to ~/.nvidia-settings-rc
```

**VRAM exhaustion** (stutter→freeze in heavy games): watch `nvidia-smi`; lower texture settings; on Wayland compositors VRAM pressure handling is worse than Windows — 8GB cards hit walls earlier.

**GSP firmware issues** (driver 530+, Turing+): random stutter/latency on some systems; toggle with `nvidia.NVreg_EnableGpuFirmware=0` (proprietary `nvidia` only, not nvidia-open which requires GSP) — 🔴 tier.

## Diagnosing

```bash
journalctl -b 0 -k | grep -iE 'nvidia|nvrm'    # driver init, Xid errors
# "Xid" lines = GPU exceptions; Xid 79 = GPU fell off bus (power/overheat),
# Xid 31/43 = page fault (app or driver bug), Xid 8/13 = often unstable OC
nvidia-smi -q -d TEMPERATURE,POWER             # thermals/power caps
cat /proc/driver/nvidia/version
```
