# Power Management Reference

## Daemon Conflict Matrix

Only ONE of these should be active at a time:

| Daemon | Conflict with | Notes |
|--------|---------------|-------|
| `power-profiles-daemon` | TLP, tuned, auto-cpufreq | Used by GNOME/KDE power UI by default |
| `tlp` | power-profiles-daemon, tuned | Most configurable; installs tlp-pd for PPD compat |
| `tuned` | power-profiles-daemon | Has `tuned-ppd` compat layer since 2.23.0 |
| `auto-cpufreq` | power-profiles-daemon | Good for laptops; dynamic AC/BAT switching |

Check active daemons:
```bash
for s in power-profiles-daemon tuned auto-cpufreq tlp; do
  printf '%s: %s\n' "$s" "$(systemctl is-active $s 2>/dev/null)"
done
```

Multiple active = conflict. Disable unused ones:
```bash
sudo systemctl disable --now <daemon>.service
sudo systemctl mask <daemon>.service  # prevent re-activation by deps
```

## TLP

### Install

**Arch:**
```bash
sudo pacman -S tlp tlp-pd tlp-rdw
sudo systemctl enable --now tlp.service
sudo systemctl enable --now tlp-pd.service  # PPD compatibility
sudo systemctl mask systemd-rfkill.service systemd-rfkill.socket
```
Note: Installing TLP removes `power-profiles-daemon`.

**Fedora 44+:**
```bash
sudo dnf install --allowerasing tlp tlp-pd tlp-rdw
# --allowerasing removes conflicting tuned + power-profiles-daemon
sudo systemctl enable --now tlp.service
sudo systemctl enable --now tlp-pd.service
sudo systemctl mask systemd-rfkill.service systemd-rfkill.socket
```

**Ubuntu/Debian (from PPA for latest):**
```bash
sudo add-apt-repository ppa:linrunner/tlp
sudo apt update
sudo apt install tlp tlp-pd tlp-rdw
sudo systemctl enable --now tlp.service
```
Note: PPA install removes `power-profiles-daemon`.

### Key CPU Settings (`/etc/tlp.conf`)

```
# CPU driver mode: active = full EPP control; passive = cpufreq only; guided = auto
CPU_DRIVER_OPMODE_ON_AC=active
CPU_DRIVER_OPMODE_ON_BAT=active

# Frequency scaling governor
CPU_SCALING_GOVERNOR_ON_AC=performance
CPU_SCALING_GOVERNOR_ON_BAT=powersave

# Energy Performance Preference (EPP)
# Values: default, performance, balance_performance, balance_power, power
CPU_ENERGY_PERF_POLICY_ON_AC=balance_performance
CPU_ENERGY_PERF_POLICY_ON_BAT=power

# Intel: max P-state % (0=min, 100=max)
CPU_MIN_PERF_ON_AC=0
CPU_MAX_PERF_ON_AC=100
CPU_MIN_PERF_ON_BAT=0
CPU_MAX_PERF_ON_BAT=80

# CPU boost (turbo)
CPU_BOOST_ON_AC=1
CPU_BOOST_ON_BAT=0
```

### Battery Care (`/etc/tlp.conf`)

```
# Charge thresholds (ThinkPads and some others — check vendor support)
START_CHARGE_THRESH_BAT0=75
STOP_CHARGE_THRESH_BAT0=80
RESTORE_THRESHOLDS_ON_BAT=1  # re-apply thresholds on unplug
```

Both start AND stop thresholds required (use 0 to skip one).

### Notes
- `amd-pstate` in passive/guided mode does NOT support EPP — need active mode
- Intel EPP and EPB are mutually exclusive; when EPP available (Skylake+), EPB ignored
- AMD: kernel 6.13+ sets initial `scaling_min_freq` to `amd_pstate_lowest_nonlinear_freq`
- AMD: kernels older than 6.5 need `amd_pstate=active` boot param to activate

## auto-cpufreq

Best for laptops: dynamically adjusts governor + turbo based on AC/BAT + CPU load.

```bash
# Arch (AUR)
paru -S auto-cpufreq
sudo systemctl enable --now auto-cpufreq

# Ubuntu/Debian (snap)
sudo snap install auto-cpufreq
sudo auto-cpufreq --install

# Fedora
sudo dnf copr enable elia-el-puente/auto-cpufreq
sudo dnf install auto-cpufreq
sudo systemctl enable --now auto-cpufreq
```

Disable PPD first: `sudo systemctl disable --now power-profiles-daemon`

## power-profiles-daemon

Default on GNOME and KDE. Minimal config; good for zero-effort setups.

Profiles: `balanced`, `power-saver`, `performance`

```bash
# Check status
powerprofilesctl get

# Switch profile
powerprofilesctl set performance
```

## tuned

Profile-based, highly configurable.

```bash
# List profiles
tuned-adm list

# Apply profile
sudo tuned-adm profile throughput-performance
sudo tuned-adm profile balanced  # for laptops

# PPD compat layer
sudo systemctl enable --now tuned-ppd  # makes tuned respond to GNOME/KDE power UI
```

Useful profiles: `latency-performance`, `throughput-performance`, `powersave`, `balanced`, `realtime` (for RT audio)

## EPP Values (Energy Performance Preference)

| EPP Value | Use Case |
|-----------|----------|
| `performance` | Max perf, max power |
| `balance_performance` | Default AC: good perf, some savings |
| `balance_power` | Balanced on battery |
| `power` | Max battery savings |

Read current EPP:
```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
```

Set (not persistent without TLP/tuned/PPD):
```bash
echo balance_performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
```
