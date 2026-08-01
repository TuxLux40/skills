# GPU Reference — AMD, Hybrid Graphics, DKMS

## AMD GPU (RDNA / GCN / RDNA2/3)

Driver stack: `amdgpu` kernel module → `radeonsi` (OpenGL) + `RADV` (Vulkan, Mesa) + optional `AMDVLK` (AMD's separate Vulkan driver).

**RADV is the default Vulkan driver on gaming distros and Steam Deck.** ACO compiler (Mesa's AMD shader backend) is enabled by default since Mesa 20.2 — faster compile times than LLVM.

### Required packages (Arch/CachyOS)

```bash
# Core driver stack
mesa           # OpenGL (radeonsi) + VA-API/VDPAU video decode
lib32-mesa     # 32-bit game support (multilib repo required)
vulkan-radeon  # RADV Vulkan driver
lib32-vulkan-radeon  # 32-bit Vulkan

# If amdgpu module doesn't load automatically
linux-firmware  # or linux-firmware-amdgpu — required for all modern AMD GPUs
```

**If GPU not recognized / wrong driver:** `lspci -k` → confirm `Kernel driver in use: amdgpu`. If it shows `radeon` on GCN1/2 hardware, add to `/etc/modprobe.d/amdgpu.conf`:
```
options amdgpu si_support=1   # GCN 1 (Southern Islands)
options amdgpu cik_support=1  # GCN 2 (Sea Islands)
options radeon si_support=0
options radeon cik_support=0
```
Then add `amdgpu` first in `/etc/mkinitcpio.conf` MODULES array and regenerate initramfs.

**amdgpu fails to load:** Check that `nomodeset` and `vga=` are NOT in kernel params (amdgpu requires KMS). Check `dmesg | grep amdgpu` for firmware errors.

### Kernel Module Parameters

Set via `/etc/modprobe.d/amdgpu.conf` or kernel cmdline. Require reboot (or `modprobe -r amdgpu && modprobe amdgpu` if no display driver is active).

| Parameter | Effect | Use when |
|-----------|--------|----------|
| `amdgpu.ppfeaturemask=0xffffffff` | Enable all PowerPlay features incl. overdrive | Overclocking/undervolting |
| `amdgpu.ppfeaturemask=0xffff7fff` | Disable GFXOFF | MCLK stuck at min/max on some RDNA cards |
| `amdgpu.dc=0` | Disable Display Core | Last resort for display init failures |
| `amdgpu.sg_display=0` | Disable scatter/gather display (APU only) | Screen flicker on resolution change or monitor reconnect |
| `amdgpu.dcdebugmask=0x10` | Disable Panel Self Refresh v1 | Display freeze/stutter on laptop panels |
| `amdgpu.dcdebugmask=0x12` | Disable PSR + memory stutter mode | More aggressive PSR fix |
| `amdgpu.gpu_recovery=1` | Enable GPU hang recovery | Games that trigger GPU hangs instead of crashing |
| `amdgpu.runpm=0` | Disable runtime power-down for dGPU | dGPU randomly going offline |
| `amdgpu.reset_method=` | GPU reset method (-1=auto, 1=mode0, 2=mode1, 4=baco) | Hard GPU hangs requiring reset |
| `amdgpu.lockup_timeout=` | GPU scheduler timeout (ms); `-1`=infinity | Timeout-triggered resets on heavy workloads |

List all available parameters: `modinfo amdgpu | grep parm`

### Power Management Sysfs

```bash
# Performance level (most impactful single knob)
cat /sys/class/drm/card0/device/power_dpm_force_performance_level
# Values: auto | low | high | manual | profile_standard | profile_min_sclk | profile_min_mclk | profile_peak
echo "high" | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level

# Power cap (in microwatts — 1W = 1,000,000 µW)
cat /sys/class/hwmon/hwmon*/power1_cap_max    # hardware maximum
cat /sys/class/hwmon/hwmon*/power1_cap_min    # hardware minimum
echo 150000000 | sudo tee /sys/class/hwmon/hwmon*/power1_cap  # set 150W cap

# Monitoring (all values via sysfs — replace card0 with card1 on multi-GPU)
cat /sys/class/drm/card0/device/gpu_busy_percent          # GPU utilization %
cat /sys/class/drm/card0/device/mem_info_vram_used        # VRAM used (bytes)
cat /sys/class/drm/card0/device/mem_info_vram_total       # VRAM total (bytes)
cat /sys/class/drm/card0/device/pp_dpm_sclk               # GPU clock states
cat /sys/class/drm/card0/device/pp_dpm_mclk               # memory clock states
cat /sys/class/hwmon/hwmon*/temp1_input                    # GPU temp (millidegrees Celsius)
cat /sys/class/hwmon/hwmon*/in0_input                      # GPU voltage (millivolts)
cat /sys/class/hwmon/hwmon*/power1_average                 # avg power draw (µW)
cat /sys/class/hwmon/hwmon*/fan1_input                     # fan speed (RPM)

# Live debug view (verbose)
sudo watch -n 0.5 cat /sys/kernel/debug/dri/0/amdgpu_pm_info

# Tools
amdgpu_top    # best live tool (package: amdgpu_top)
radeontop     # older alternative
sensors       # also reads hwmon; needs lm_sensors

# Fan control (use ONE method, not both simultaneously)
echo 1 | sudo tee /sys/class/hwmon/hwmon*/pwm1_enable    # manual fan control
echo 200 | sudo tee /sys/class/hwmon/hwmon*/pwm1         # set fan speed 0-255
echo 2 | sudo tee /sys/class/hwmon/hwmon*/pwm1_enable    # back to auto

# Manual clock/voltage tuning (requires ppfeaturemask=0xffffffff)
# First: echo manual > power_dpm_force_performance_level
cat /sys/class/drm/card0/device/pp_od_clk_voltage         # current OC table
# Write "s 1 1800 900" → set sclk level 1 to 1800 MHz at 900mV
# Write "m 0 875" → set mclk level 0 to 875 MHz
# Write "c" → commit changes
```

**GDDR6 memory clock conversion:** effective_clock = controller_clock × 2; data_rate = effective_clock × 8 (MT/s).

**profile_peak** mode: disables all clock gating and power gating — max clocks, recommended for benchmarking, not daily use.

### Known AMD Hardware Issues

| Symptom | GPU family | Fix |
|---------|-----------|-----|
| Full system freeze while gaming | Vega | Force `high` perf level; fixed in kernel 6.12.9+ |
| MCLK stuck at 96 MHz or max | RDNA (various) | `amdgpu.ppfeaturemask=0xffff7fff` (disables GFXOFF) |
| Screen flicker when reconnecting monitor | APUs | `amdgpu.sg_display=0` |
| Display freezes intermittently | Laptops with PSR | `amdgpu.dcdebugmask=0x10` |
| VRR + HDR stutter simultaneously | RDNA2/3 in gamescope | Requires `AMD_PRIVATE_COLOR` kernel build or Steam Deck kernel — 🔴 Deep (see `display.md`) |
| R9 390 poor performance | Sea Islands | `radeon.cik_support=0 amdgpu.cik_support=1 amdgpu.dc=1` |

### Diagnosing GPU Issues

```bash
dmesg | grep -i amdgpu                          # GPU driver messages, hangs, resets
dmesg | grep -iE 'gpu|drm|amdgpu|reset|hang'
journalctl -b 0 | grep -iE 'amdgpu|drm|gpu'    # current boot
amdgpu_top                                       # live utilization, clocks, power
```

**Hung GPU indicator:** `dmesg` shows `amdgpu: GPU recovered successfully` or `amdgpu: ring gfx timeout`. If no recovery, system hard-freezes.

### RADV / Vulkan

```bash
vulkaninfo --summary             # check RADV is detected
MESA_VK_DEVICE_SELECT=...        # force specific GPU (multi-GPU setups)
RADV_PERFTEST=transfer_queue     # enable dedicated SDMA transfer queue (Mesa 26+, GFX9+); helps DXVK
```

## Hybrid Graphics (Multi-GPU Laptops)

Laptops with both iGPU (Intel/AMD integrated) and dGPU (NVIDIA/AMD discrete). The iGPU always runs; dGPU is powered on demand.

### PRIME (AMD dGPU or NVIDIA with nouveau)

```bash
# Run a single app on the discrete GPU
DRI_PRIME=1 game                              # AMD dGPU via PRIME
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia game   # NVIDIA proprietary

# Steam launch option for discrete GPU
DRI_PRIME=1 %command%
# or for NVIDIA proprietary:
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia %command%

# Verify which GPU is being used
glxinfo | grep "OpenGL renderer"
```

### Force discrete GPU for all games (BIOS/display mux)

Some laptops have a MUX switch (BIOS setting or software) that routes display directly through dGPU — eliminates iGPU overhead, maximum gaming performance.

### Power down discrete GPU completely (laptops)

When not gaming, dGPU draws power even idle. Options:
1. **BIOS toggle** — some manufacturers expose dGPU disable in UEFI
2. **udev rules** — remove NVIDIA PCI device at boot (NVIDIA-specific)
3. **bbswitch** — NVIDIA automatic on/off (doesn't work with kernel ≥4.8 PCIe PM)
4. **acpi_call** — manual ACPI calls, find working call with `/usr/share/acpi_call/examples/turn_off_gpu.sh`

```bash
# acpi_call: find working OFF call
sudo modprobe acpi_call
sudo /usr/share/acpi_call/examples/turn_off_gpu.sh
# Note the line that says "works!" — use that path for permanent setup
```

**Persist acpi_call at boot:**
```
# /etc/tmpfiles.d/acpi_call.conf
w /proc/acpi/call - - - - \_SB.PCI0.PEG0.PEGP._OFF
```

### Selecting GPU for Vulkan / gamescope

```bash
MESA_VK_DEVICE_SELECT=1002:xxxx %command%   # AMD (use PCI ID from lspci)
MESA_VK_DEVICE_SELECT=pci:0000:01:00        # by PCI slot
vulkaninfo --summary | grep deviceName      # list detected GPUs
```

## Kernel Module Management (DKMS)

After kernel upgrades, out-of-tree modules (custom drivers, `v4l2loopback`, GPU firmware patches) must be rebuilt. DKMS does this automatically when installed.

```bash
dkms status                    # list all DKMS modules + build status
dkms autoinstall               # rebuild all for current running kernel
dkms autoinstall -k 6.x.x-1   # rebuild for specific kernel
```

If a DKMS build fails after a kernel upgrade, check:
1. `pacman -S linux-headers` (or `linux-cachyos-headers` etc.) — headers must match kernel
2. `journalctl -b 0 | grep dkms` for build errors
