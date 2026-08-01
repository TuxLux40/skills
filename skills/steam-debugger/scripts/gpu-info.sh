#!/bin/sh
# gpu-info.sh — read-only GPU state snapshot: driver binding, Vulkan devices,
# AMD sysfs power/clock/VRAM/thermal state, kernel GPU errors. Mutates nothing.

LC_ALL=C; export LC_ALL   # stable output for parsing regardless of system locale

have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n=== %s ===\n' "$1"; }

section "PCI GPUs + kernel driver in use"
if have lspci; then
    lspci -k 2>/dev/null | grep -A3 -E 'VGA|3D|Display'
else
    echo "(skipped: lspci not found — install pciutils)"
fi

section "Vulkan devices"
if have vulkaninfo; then
    vulkaninfo --summary 2>/dev/null | grep -E 'deviceName|deviceType|driverName|driverInfo|apiVersion' || echo "(vulkaninfo produced no device output)"
else
    echo "(skipped: vulkaninfo not found — install vulkan-tools)"
fi

section "OpenGL renderer"
if have glxinfo; then
    glxinfo 2>/dev/null | grep -E 'OpenGL renderer|OpenGL version' || echo "(no X/GL context available)"
else
    echo "(skipped: glxinfo not found — install mesa-utils / mesa-demos)"
fi

section "AMD sysfs state (per card)"
found_amd=0
for card in /sys/class/drm/card[0-9]; do
    [ -e "$card/device/power_dpm_force_performance_level" ] || continue
    found_amd=1
    name=$(basename "$card")
    echo "--- $name ---"
    printf 'perf level:   %s\n' "$(cat "$card/device/power_dpm_force_performance_level" 2>/dev/null)"
    printf 'gpu busy:     %s%%\n' "$(cat "$card/device/gpu_busy_percent" 2>/dev/null)"
    vu=$(cat "$card/device/mem_info_vram_used" 2>/dev/null)
    vt=$(cat "$card/device/mem_info_vram_total" 2>/dev/null)
    [ -n "$vu" ] && [ -n "$vt" ] && printf 'vram:         %s / %s MiB\n' "$((vu/1048576))" "$((vt/1048576))"
    echo 'sclk states:'
    cat "$card/device/pp_dpm_sclk" 2>/dev/null | sed 's/^/  /'
    echo 'mclk states:'
    cat "$card/device/pp_dpm_mclk" 2>/dev/null | sed 's/^/  /'
done
[ "$found_amd" = 0 ] && echo "(no amdgpu sysfs interfaces found — not an AMD GPU or driver not loaded)"

section "hwmon thermals/power (all sensors)"
for hw in /sys/class/hwmon/hwmon*; do
    [ -e "$hw/name" ] || continue
    nm=$(cat "$hw/name" 2>/dev/null)
    t=$(cat "$hw/temp1_input" 2>/dev/null)
    p=$(cat "$hw/power1_average" 2>/dev/null)
    f=$(cat "$hw/fan1_input" 2>/dev/null)
    line="$nm:"
    [ -n "$t" ] && line="$line temp=$((t/1000))°C"
    [ -n "$p" ] && line="$line power=$((p/1000000))W"
    [ -n "$f" ] && line="$line fan=${f}rpm"
    echo "$line"
done

section "kernel GPU messages (errors/hangs/resets)"
if have journalctl; then
    journalctl -b 0 -k --no-pager 2>/dev/null \
        | grep -iE 'amdgpu.*(error|fail|timeout|hang|reset|recover)|drm.*(error|fail)|nvidia.*(error|fail)|i915.*(error|fail)' \
        | tail -30
    [ $? -ne 0 ] && echo "(no GPU errors in current boot, or journal not readable — try sudo)"
elif have dmesg; then
    dmesg 2>/dev/null | grep -iE 'amdgpu|drm' | tail -30 || echo "(dmesg not readable — try sudo)"
else
    echo "(skipped: no journalctl/dmesg)"
fi

echo
echo "Done. Interpret with steam-debugger reference/gpu.md."
