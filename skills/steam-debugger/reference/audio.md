# Audio — PipeWire, WirePlumber, ALSA

Steam gaming distros use **PipeWire** (with PulseAudio compatibility layer). Most gaming audio issues are prefix-level (missing xaudio2/dsound) not system-level.

Steam uses **SDL 2.0** for audio/windowing in Valve games. Non-Valve games typically use xaudio2, dsound, or openal — each may need separate installation into the Wine prefix (see `wine-proton.md`).

## PipeWire architecture

```
Application (PulseAudio API / ALSA API / JACK API)
       ↓
pipewire-pulse / pipewire-alsa / pipewire-jack  (compatibility bridges)
       ↓
PipeWire daemon (pipewire.service)
       ↓
WirePlumber (wireplumber.service — session manager, handles routing)
       ↓
ALSA → hardware
```

**Required packages:**
- `pipewire pipewire-audio` — core daemon
- `pipewire-pulse` — PulseAudio compatibility (replaces pulseaudio)
- `pipewire-alsa` — ALSA compatibility (required for FMOD games!)
- `pipewire-jack` — JACK compatibility
- `wireplumber` — session manager
- `lib32-pipewire` — 32-bit audio for 32-bit games
- `lib32-pipewire-jack` — 32-bit JACK

**Verify PipeWire is running:**
```bash
pactl info | grep "Server Name"   # should show "PulseAudio (on PipeWire x.y.z)"
systemctl --user status pipewire.service wireplumber.service
```

## PipeWire config locations

**Never edit `/usr/share/pipewire/` or `/usr/share/wireplumber/`** — overwritten on package update.

| Scope | Path |
|-------|------|
| System PipeWire override | `/etc/pipewire/` |
| User PipeWire override | `~/.config/pipewire/` |
| System WirePlumber override | `/etc/wireplumber/wireplumber.conf.d/` |
| User WirePlumber override | `~/.config/wireplumber/wireplumber.conf.d/` |

After config change: `systemctl --user restart wireplumber.service`

WirePlumber config format changed in v0.5: `.lua` → `.conf`. See migration docs if upgrading from older systems.

**Bluetooth A2DP/HSP auto-switch:** WirePlumber auto-switches between A2DP (high quality, output only) and HSP/HFP (microphone + output, lower quality) when a mic input stream is detected. Disable with `wpctl`.

## Common audio failures

| Symptom | Fix tier | Fix |
|---------|----------|-----|
| No sound in game | ✅ Official | `protontricks <appid> xact` (installs xaudio2); or `WINEDLLOVERRIDES=xaudio2_7=n,b %command%` |
| Crackling / popping in Wine/Proton | ✅ Official | Same; or upgrade Proton (fixed in 3.16-5+) |
| Audio works in menu, not gameplay | ✅ Official | Different audio path in-game — check ProtonDB |
| No audio in gamescope session | ⚠️ Unofficial | `systemctl --user status pipewire.service`; check `WantedBy` target is correct (see `session-architecture.md`) |
| No audio in FMOD games (Project Zomboid, Don't Starve Together, Hotline Miami, Transistor) | ✅ Official | Install `pipewire-alsa` — FMOD uses ALSA API directly |
| Wine/Proton crackling on Steam Deck OLED | ✅ Supported | `default.clock.min-quantum = 256` in WirePlumber config (256=minimum working; 512 or 1024 safer) |
| Wrong audio device used | ✅ Official | `pactl set-default-sink <device-name>` |
| No 32-bit game audio | ✅ Official | Install `lib32-pipewire` |
| FMOD crackling on specific card (Hotline Miami) | ✅ Official | Set correct default ALSA card in `/etc/asound.conf` |
| OpenAL can't move streams between devices | ✅ Official | Add `[pulse]\nallow-moves=true` to `~/.alsoftrc` |
| Crackling mic in Steam Voice / games | ✅ Official | `PULSE_LATENCY_MSEC=30 %command%` |
| Old Steam runtime ALSA conflict | ⚠️ Unofficial | Rename `~/.steam/steam/ubuntu12_32/steam-runtime/i386/usr/lib/i386-linux-gnu/alsa-lib/`; or `LD_PRELOAD='/usr/$LIB/libasound.so.2' steam` |

**Min-quantum config example** (for OLED Deck / Wine crackling):
```bash
mkdir -p ~/.config/wireplumber/wireplumber.conf.d/
cat > ~/.config/wireplumber/wireplumber.conf.d/51-quantum.conf << 'EOF'
monitor.alsa.rules = [
  {
    matches = [{ node.name = "~alsa_output.*" }]
    actions = { update-props = { audio.rate = 48000, audio.allowed-rates = "32000,44100,48000", clock.min-quantum = 256 } }
  }
]
EOF
systemctl --user restart wireplumber.service
```

**Set sink volume:**
```bash
pactl get-sink-volume @DEFAULT_SINK@
pactl set-sink-volume @DEFAULT_SINK@ 75%
pactl set-sink-volume @DEFAULT_SINK@ 100% 75%   # per-channel (L R)
pactl list sinks | grep -B1 -A9 State:           # list all sinks
```

**Audio isolation (OBS/streaming):** create virtual sink for game-only audio:
```bash
pactl load-module module-null-sink sink_name=game_audio
# Route game to game_audio sink, OBS captures game_audio.monitor
```

## ALSA troubleshooting (when PipeWire doesn't abstract fully)

```bash
alsamixer                     # visual mixer (F6 = select card, F4 = capture channels)
alsactl restore               # restore saved ALSA state (fixes muted-after-reboot)
alsa-info.sh                  # diagnostic script (run as root, share output for help)
speaker-test                  # test playback

# Check which ALSA card is default
cat /proc/asound/cards
aplay -l                      # list playback devices
arecord -L                    # list capture devices (long format)

# Test microphone
arecord --duration=5 --format=dat test-mic.wav && aplay test-mic.wav
arecord -vv --format=dat /dev/null   # with verbose level meter
```

**Default card override** — `~/.asoundrc` to override default capture device (e.g. USB webcam mic while keeping default playback):
```
pcm.usb { type hw; card U0x46d0x81d }
pcm.!default {
    type asym
    playback.pcm { type plug; slave.pcm "dmix" }
    capture.pcm  { type plug; slave.pcm "usb" }
}
```

**Volume too low even at max:** add softvol plugin to `/etc/asound.conf`:
```
pcm.!default { type plug; slave.pcm "softvol" }
pcm.softvol {
    type softvol; slave { pcm "dmix" }
    control { name "Pre-Amp"; card 0 }
    min_dB -5.0; max_dB 20.0; resolution 6
}
```

**Crackling through headphone jack:** mute Mic channel in alsamixer (`amixer sset "Mic" 0%` or `mute`).

**Multiple sound cards / wrong card at boot:** set default in `/etc/asound.conf`:
```
defaults.pcm.card 1
defaults.ctl.card 1
```
