# Tribal Knowledge — Anecdotal Fixes (🟣 Last Resort)

Fixes from community discussion that worked for real users but have **no official documentation**. Consult only after the ✅ and ⚠️ fixes for the symptom have failed. Always disclose to the user that a fix from this file is anecdotal and cite its provenance line.

## Entry format

Every entry must carry provenance — an unsourced tribal fix is a rumor, not knowledge:

```markdown
### <symptom, phrased as user would say it>
- **Fix:** <exact commands/config>
- **Reversal:** <how to undo it>
- **Source:** <Discord server + channel / forum thread URL>, <date>
- **Confirmations:** <how many independent users reported it working>
- **Suspected mechanism:** <best guess why it works, or "unknown">
```

Entries with unknown mechanism are still valid — that is the nature of tribal knowledge — but say so explicitly.

## Maintenance rules

- When an official fix later lands (kernel patch, package update, wiki documentation), **move the knowledge to the appropriate reference file** at ✅/⚠️ tier and delete the entry here, noting the version that fixed it.
- Prefer entries that are reversible. Irreversible anecdotal fixes need a strong confirmation count and an explicit warning.
- Date matters: an entry older than ~2 years on a rolling-release distro is suspect — verify the underlying component still exists before suggesting it.

## Entries

### "Graphics device is invalid, please run the configuration tool" (old D3D9 games)
- **Fix:** The game validates a Direct3D 9 adapter GUID stored in its config file against what DXVK returns from `IDirect3D9::GetAdapterIdentifier()`. Run the game's own configuration tool *inside the same Proton prefix* so DXVK enumerates the real GPU and writes a valid GUID: `protontricks-launch --appid <APPID> <ConfigTool>.exe`, select the GPU in its dropdown, save. An all-zeros GUID is NOT a valid fallback — "clearing" the field does not work.
- **Reversal:** Config file is plain text — back it up before running the tool. Note: many config tools reset graphics settings to minimum when they save; restore settings afterwards.
- **Source:** Local debugging session (Binary Domain, AppID 203750), 2026-05/06, CachyOS + RADV + GE-Proton10
- **Confirmations:** 1 (deep root-cause analysis, verified by PROTON_LOG)
- **Suspected mechanism:** Confirmed — GUID equality check at startup; pattern likely shared by other D3D9-era Japanese ports

### No sound in games using CRI middleware (Yakuza-engine / SEGA ports)
- **Fix:** CRI Audio middleware loads `xaudio2_7.dll` at runtime via `LoadLibrary()`; Proton's FAudio substitute doesn't satisfy it. `protontricks <APPID> xact` (installs real Microsoft XAudio2/XACT DLLs as native,builtin) plus launch option `WINEDLLOVERRIDES=xaudio2_7=n,b %command%` as runtime backup. Verify with `PROTON_LOG=1`: the `xaudio2_7.dll` LoadLibrary call must resolve `native`, not `builtin`.
- **Reversal:** Remove launch option; `protontricks <APPID> --gui` → remove overrides, or nuclear prefix reset.
- **Source:** Local debugging session (Binary Domain), 2026-05/06; xact fix itself is widely documented — the CRI mechanism detail and the verification method are the tribal part. A `DSOUND` import in the game binary is a red herring; actual audio path is XAudio2 via CRI.
- **Confirmations:** 1 local + widespread community use of xact for SEGA ports
- **Suspected mechanism:** Confirmed via binary inspection (`CriAuVoice`, `ADXXAUDIO2` strings)

### Gamepad works in menus but not in gameplay
- **Fix:** Menu input and gameplay input use different code paths in some ports — gameplay polls raw XInput, which Steam Input intercepts and re-emits via its virtual device, leaving the raw path empty. Disable Steam Input for the game (Properties → Controller, or `SteamInput=2` in `localconfig.vdf`). Steam must be FULLY closed before editing `localconfig.vdf` — Steam rewrites it on exit, silently reverting your edit.
- **Reversal:** Re-enable Steam Input per-game.
- **Source:** Local debugging session (Binary Domain) + Steam community thread `steamcommunity.com/app/203750/discussions/0/142261027578527962/`
- **Confirmations:** 2+ (local + community thread)
- **Suspected mechanism:** Confirmed — split input paths; some PC ports additionally have native controller bugs no Linux fix can solve

### Controller Settings screen is completely blank (no Edit Layout button, Steam Input enabled)
- **Fix:** The gamepadui "Controller Settings" panel renders as an empty shell (title bar + MENU/SELECT/BACK footer only — no "Current Button Layout" card, no View/Edit Layout buttons) when the game's per-app controller config selection has resolved to nothing, so Steam silently falls back to the generic built-in template (`controller_base/templates/controller_neptune_gamepad_fps.vdf`) instead of a real personal/Community/developer layout. Confirm via `~/.steam/steam/logs/controller_ui.txt`: grep for `Loaded Config for Local Selection Path for App ID <appid>` — a path under `controller_base/templates/` means the broken fallback state; a path under `Steam Controller Configs/<userid>/config/<appid>/` (personal) or `steamapps/workshop/content/241100/` (Community/Official) means a real config is assigned and the panel should render fine. Steam Input being enabled/disabled for the app is unrelated and does not fix this. Fix: clear the stale selection so Steam re-resolves it — via Steam's own CEF remote-debugging port (CDP), evaluate `SteamClient.Input.ClearSelectedConfigForApp(<appid>, 0)` against the `SharedJSContext` target, then reopen Controller Settings (`SteamClient.Apps.ShowControllerConfigurator(<appid>)`). There is no in-UI button for this — the panel that would normally expose "change layout" is the one that's blank.
- **Reversal:** n/a — only clears a selection pointer, does not delete any saved personal binding. Worst case Steam re-resolves to the same generic template it was already using.
- **Source:** Local debugging session (HITMAN World of Assassination, AppID 1659040) via decky-claude MCP `steam_ui_eval` (CDP into Steam's embedded CEF), 2026-09-13
- **Confirmations:** 1 (reproduced twice: once via the interactive session, once via a standalone script hitting the raw CDP websocket independently)
- **Suspected mechanism:** Unconfirmed at the Steam source level (closed-source client) — appears to be a frontend render bug in the gamepadui React panel when the resolved config carries no display metadata (title/icon) to bind to. `SteamClient.Input` has no public documentation; `ClearSelectedConfigForApp` and `QueryControllerConfigsForApp` were discovered by enumerating `Object.keys(SteamClient.Input)` at runtime. Note: a game-specific "Controller Layout" popup window only exposes a minimal `SteamClient.Input` subset (input/touch-menu registration) — the config-management calls must be run against `SharedJSContext`, not the popup.

### Steam overlay (store page / browser) stuck visible after closing it, input already reaches the game fine
- **Fix:** This looks like an input-focus bug but isn't one — the game is receiving controller/keyboard input correctly the whole time (menu navigation, sounds, etc. all work); what's stuck is purely a compositor/render leftover. Two layers to clear, in order:
  1. The overlay's actual page target (e.g. titled `"<Game Name> on Steam"`, URL `store.steampowered.com/app/<appid>/...` in `steam_ui_targets`) may still be alive even though `SteamClient.Overlay.GetOverlayBrowserInfo()` already reports zero active overlay browsers — Steam's own bookkeeping loses track of it before the render does. The DOM's own `window.close()` run inside that page is a silent no-op (Chromium blocks self-close on windows not opened via script). What actually works: that page has a **self-scoped** `SteamClient.Window` API — call `SteamClient.Window.Close()` with `target` set to that specific page (not `SharedJSContext`, and not `Window.Close()` with a manually-guessed window ID, which risks closing an unrelated window such as Big Picture's own root). This tears down the CDP target for the overlay content cleanly.
  2. Even after that, a residual `<div id="header" class="...FlexGrowWebBrowserURLBar...">` element inside the `"Steam Big Picture Mode"` root page can remain `visible: true` (its sibling `.FullModalOverlay`/`.ModalOverlayBackground` wrapper correctly flips to `visible: false`, but this header div doesn't unmount with it) — the browser toolbar chrome (URL bar, back/forward, the bottom `MENU`/`B BACK` hint bar) is a separate component from the content view and isn't reliably torn down atomically with it. Force-hide it directly: `document.getElementById('header').style.display = 'none'` run against the `"Steam Big Picture Mode"` target.
  - **Tooling caveat:** the `screenshot` MCP tool (DRM/compositor capture) did not show this stuck overlay at all across repeated attempts, even though it was confirmed on the physical display via a phone photo from the user. Don't trust a clean `screenshot` result alone to mean "no overlay" on a gamescope-session desktop setup — cross-check with `steam_ui_targets` / `GetOverlayBrowserInfo()`, or ask for a real-device photo, before concluding there's nothing there.
- **Reversal:** n/a — both steps are transient: step 1 closes a browser view the user was trying to close anyway; step 2 is a live DOM style override with nothing persisted to disk. Reopening any overlay causes Steam to re-render its own header normally.
- **Source:** Local debugging session (Tomb Raider (2013) GOTY, AppID 203160) via decky-claude MCP `steam_ui_eval` (CDP into Steam's embedded CEF), gamescope-session desktop (not Steam Deck), 2026-09-22
- **Confirmations:** 1 (this session; visually confirmed before/after via user-supplied phone photos, since the `screenshot` tool never captured the overlay layer itself)
- **Suspected mechanism:** Unconfirmed at the Steam source level (closed-source client) — the overlay's content `BrowserView` and its toolbar/header component appear to be separate UI elements with independent lifecycles; closing the content view doesn't reliably also unmount the header, leaving it stuck rendered until manually hidden.

### Game config persists across prefix wipes (config not in prefix)
- **Fix:** Not a fix — a diagnostic trap. Some games write config into their *steamapps install directory* (e.g. `steamapps/common/<Game>/savedata/`), not the Proton prefix. Nuclear prefix reset will NOT clear such config; if a bad config value causes the failure, the reset appears to "not work." Check the game directory for config/savedata files before concluding the prefix reset failed.
- **Reversal:** n/a (diagnostic guidance)
- **Source:** Local debugging session (Binary Domain `UserCFG.txt`), 2026-05/06
- **Confirmations:** 1
- **Suspected mechanism:** Confirmed — game uses working-directory-relative config path
