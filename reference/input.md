# Input — Controllers, udev, Steam Input

## Baseline setup (do this first)

Most "controller not detected" issues are **missing udev rules**, not drivers:

```bash
# Arch/CachyOS: package with Valve's canonical udev rules
pacman -S game-devices-udev        # community package, covers ~all pads
# Upstream source of those rules:
# https://github.com/ValveSoftware/steam-devices
# After install: replug controller or
sudo udevadm control --reload && sudo udevadm trigger
```

Test detection layers in order:
```bash
# 1. Kernel sees it?
dmesg | tail -20                   # after plugging in
ls /dev/input/js* /dev/input/event*
# 2. evdev sees it?
evtest                             # select device, press buttons (package: evtest)
# 3. SDL sees it? (what most games use)
sdl2-jstest --list                 # package: sdl2-jstest / joyutils
# 4. Steam sees it? Steam → Settings → Controller
```

The layer where detection stops tells you where the problem is: kernel = driver/udev, evdev = permissions, SDL = mapping, Steam-only = Steam Input config.

## Per-controller reference

| Controller | Kernel driver | Notes |
|-----------|--------------|-------|
| Xbox 360 (wired/wireless) | `xpad` (in-tree) | Works out of the box |
| Xbox One/Series — USB | `xpad` | Works out of the box |
| Xbox One S / Series X\|S — Bluetooth | **`xpadneo`** (DKMS: `xpadneo-dkms`) | In-tree `xpad` gives wrong mappings over BT; xpadneo adds correct mapping, battery level, trigger rumble |
| Xbox — Wireless Adapter dongle | **`xone`** (DKMS) | Dongle unsupported in-tree; xone replaces xpad for dongle use |
| DualShock 4 | `hid_sony` / `hid_playstation` (in-tree) | Works OOTB incl. Bluetooth; touchpad = mouse by default |
| DualSense (PS5) | `hid_playstation` (kernel 5.12+) | Works OOTB; adaptive triggers/haptics only in games using Steam Input or SDL 2.0.14+ |
| Steam Controller | `hid_steam` | Needs Steam or `sc-controller` running for full function; lizard mode otherwise |
| Switch Pro Controller | `hid_nintendo` (kernel 5.16+) | OOTB; older kernels: `joycond` |
| 8BitDo (all) | varies by mode | Set controller mode (X-input/D-input/Switch) BEFORE pairing; X-input mode → treated as Xbox pad |
| Generic/cheap pads | `xpad` or none | Often need SDL mapping override (see below) |

**Xbox controller connect/disconnect loop over Bluetooth:** controller firmware bug — update firmware via Xbox Accessories app (Windows or Xbox console), then re-pair. Also disable ERTM if old firmware: `echo 1 | sudo tee /sys/module/bluetooth/parameters/disable_ertm` (🔴 affects all BT).

**Third-party Xbox pad detected but no input:** switch from `xpad` to `xpadneo`.

**DS4 motion sensors hijacking joystick input** (game reads accelerometer as stick): the controller exposes multiple event devices; hide the motion device from the game or use Steam Input to remap.

## The double-input problem (very common)

**Symptom:** menu cursor jumps two entries per press, character moves on its own, or game shows two controllers.

**Cause:** Steam Input creates a *virtual* Xbox controller and is supposed to hide the physical device from the game. When hiding fails (missing udev rules, Flatpak device permissions, game reading `/dev/input` directly), the game sees **both** physical and virtual pads.

**Fixes, in order:**
1. Install `game-devices-udev` (gives Steam the device access it needs to hide the original)
2. Per-game: Properties → Controller → "Disable Steam Input" — game gets only the physical pad
3. Or the opposite: force Steam Input on, so only the virtual pad exists
4. `SteamInput=2` in `localconfig.vdf` for stubborn titles (⚠️ tier)

## Steam Input vs native

| Mode | When |
|------|------|
| **Steam Input on** | Pads the game doesn't natively support, gyro aim, per-game rebinding, Steam Controller |
| **Steam Input off** | Game has native support for your exact pad and you want vendor features (DualSense haptics in native-supporting games) |

Outside Steam: `sc-controller` (maintained fork: C0rn3j/sc-controller) provides Steam-Input-like remapping/gyro without Steam running.

## SDL mapping override (generic pads, wrong button layout)

SDL games read controller layout from a mapping database. Fix wrong layouts:

```bash
# Generate a mapping interactively
controllermap 0          # part of sdl2-jstest / SDL2 tools
# Use it per-game
SDL_GAMECONTROLLERCONFIG="<mapping string>" %command%
```
Community database (huge, check before making your own): `github.com/mdqinc/SDL_GameControllerDB` — use via:
```bash
SDL_GAMECONTROLLERCONFIG_FILE=/path/to/gamecontrollerdb.txt %command%
```

## Controller works in desktop mode, not in gaming mode (or reverse)

- Gaming mode: gamescope grabs input devices directly — overlays/remappers running only in the desktop session (AntiMicroX, input-remapper) don't apply
- `input-remapper` daemon can conflict with Steam Input — stop it when debugging: `systemctl stop input-remapper`
- Flatpak Steam: device permission may block controller — `flatpak override --user --device=input com.valvesoftware.Steam` (newer runtimes) or `--device=all`

## Polling rate

High-polling-rate mice (2000Hz+) cause stutter in gamescope — set to 1000Hz (vendor tool, `piper`/`libratbag` for many gaming mice, `solaar` for Logitech). Same applies to some controllers in wired mode.
