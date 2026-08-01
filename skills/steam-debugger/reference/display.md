# Display — Gamescope Issues, HDR, Raytracing, Color Management

## Gamescope-Specific Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No CAP_SYS_NICE, falling back to regular-priority…" in log | `sudo setcap 'CAP_SYS_NICE=eip' $(which gamescope)` ⚠️ Disables `MESA_VK_DEVICE_SELECT`; also breaks Steam Overlay |
| Mouse cursor not captured by game (camera won't lock) | Add `--force-grab-cursor` to gamescope flags |
| Low performance when pressing Meta+F (fullscreen toggle) | Launch with `-f` flag instead of toggling after launch |
| Stuttering / freezes with high-polling-rate mouse (4000Hz) | Set mouse to 1000Hz polling rate |
| VRR + HDR work separately but stutter together (AMD) | Requires `AMD_PRIVATE_COLOR` kernel build or Steam Deck kernel (linux-neptune-65) — 🔴 Deep |
| Intel graphics: corrupted/wrong image colors | `INTEL_DEBUG=nocc` (disables lossless color compression — increases memory bandwidth) |
| NVIDIA: Flatpak gamescope window doesn't appear | `flatpak override --env=GBM_BACKENDS_PATH=/usr/lib/x86_64-linux-gnu/GL/nvidia-XXX-YY-ZZ/extra/gbm <id>` |
| Swapchain errors with MangoHud | Use `--mangoapp` on gamescope, not `mangohud %command%` |
| Record gamescope output | `gst-launch-1.0 --eos-on-shutdown pipewiresrc do-timestamp=true target-object=gamescope ! vaapih264enc ! h264parse ! mux. pulsesrc do-timestamp=true device="Recording_$(pactl get-default-sink).monitor" ! opusenc ! mux. matroskamux name=mux ! filesink location=recording.mkv` |

## HDR

HDR on Linux requires gamescope (embedded/KMS mode only) + DXVK 2.1+/VKD3D-Proton 2.8+. **NVIDIA has known critical issues with gamescope HDR — AMD recommended.**

### Requirements per component

| Component | Minimum version |
|-----------|----------------|
| DXVK (D3D9–D3D11) | 2.1+ |
| VKD3D-Proton (D3D12) | 2.8+ |
| Proton (Valve) | 8.0+ |
| GE-Proton | 44+ (Proton GE 44) |
| Mesa / RADV | 25.1+ (includes `VK_EXT_swapchain_colorspace` + `VK_EXT_hdr_metadata` by default) |

### Launch options by Proton variant

```bash
# GE-Proton (proton-ge-custom)
PROTON_ENABLE_HDR=1 %command%
# Note: PROTON_ENABLE_HDR=1 internally sets DXVK_HDR=1 in GE-Proton

# proton-cachyos or wine-cachyos
PROTON_ENABLE_WAYLAND=1 DXVK_HDR=1 %command%

# wine-tkg (direct)
DXVK_HDR=1 %command%    # and unset DISPLAY

# Enable HDR for a single game under gamescope
DXVK_HDR=1 gamescope -f --hdr-enabled -- %command%
```

⚠️ Do NOT set `ENABLE_HDR_WSI=1` when using gamescope — it conflicts with `frog-color-management-v1` and breaks HDR compositing.

### gamescope-session HDR config

Optional file: `~/.config/environment.d/gamescope-session.conf`

```bash
if [ "$XDG_SESSION_DESKTOP" = "gamescope" ] ; then
    SCREEN_WIDTH=1920
    SCREEN_HEIGHT=1080
    CONNECTOR=*,eDP-1
    CLIENTCMD="steam -gamepadui -pipewire-dmabuf"
    GAMESCOPECMD="/usr/bin/gamescope --hdr-enabled --hdr-itm-enable \
    --hide-cursor-delay 3000 --fade-out-duration 200 --xwayland-count 2 \
    -W $SCREEN_WIDTH -H $SCREEN_HEIGHT -O $CONNECTOR"
fi
```

Adjust `SCREEN_WIDTH`/`SCREEN_HEIGHT` to your display. `CONNECTOR` selects output (`xrandr --query` to list). `--hdr-itm-enable` = inverse tone mapping for SDR content in HDR mode.

### Enabling in Steam

After starting gamescope with `--hdr-enabled`: Settings → Display → Enable HDR + Experimental HDR Support. Set game's Compatibility to Proton 8.0+. Set Game Resolution to native monitor resolution.

### VRR + HDR simultaneously (AMD)

These conflict at the compositor level on standard kernels. Fix requires either:
- `AMD_PRIVATE_COLOR` kernel build (e.g. `linux-amd-color` AUR, Linux 6.8+) — 🔴 Deep
- Steam Deck kernel (`linux-neptune-65` AUR or `linux-cachyos-deckify-native` AUR) — 🔴 Deep

## Hardware Raytracing

| GPU vendor | Status | Required setup |
|-----------|--------|---------------|
| **AMD RDNA2+** (RX 6000+) | ✅ Mesa 23.2+ auto-enabled | Mesa <23.2: `RADV_PERFTEST='rt'` launch option |
| **AMD RDNA1** (RX 5000) | ⚠️ Partial | `RADV_PERFTEST='rt'` but limited hardware; poor perf expected |
| **Intel Arc** (DG2+) | ✅ Supported | `VKD3D_CONFIG=dxr11,dxr` launch option (vkd3d-proton) |
| **NVIDIA RTX** | ✅ Auto in Proton 8+ | No extra flags needed; vkd3d ≥2.11 auto-enables |

**Check if raytracing is active:** Look for `Ray Tracing` in DXVK/VKD3D log (`PROTON_LOG=1 %command%`).

## Wayland Color Management Protocol

**`xx-color-management-v4`** (formerly staging MR !14 in wayland-protocols) — **merged Feb 13, 2025** into wayland-protocols main.

Enables: clients to know color properties of outputs; clients to declare their content's color profile; compositor performs automatic color management (HDR, wide-gamut, ICC profiles).

**Compositor implementations:**
- KWin (KDE): v4 — `https://invent.kde.org/plasma/kwin/-/merge_requests/6711`
- wlroots: v4 — merged
- Mutter (GNOME): v4 — `gitlab.gnome.org/GNOME/mutter/-/merge_requests/3893`
- Weston: v4 — merged

**Client implementations:**
- Mesa/Vulkan: merged
- mpv: `--vo=dmabuf-wayland`
- GStreamer: merged
- GTK4: `gitlab.gnome.org/GNOME/gtk/-/merge_requests/7489`
- Qt/KWayland: in review

**Impact for gaming:** this is the foundation of proper HDR on Wayland without gamescope. Once adopted, compositors can handle HDR natively without requiring gamescope embedded mode.

**Additional color/HDR protocol docs:** `https://gitlab.freedesktop.org/pq/color-and-hdr`
