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

### Game config persists across prefix wipes (config not in prefix)
- **Fix:** Not a fix — a diagnostic trap. Some games write config into their *steamapps install directory* (e.g. `steamapps/common/<Game>/savedata/`), not the Proton prefix. Nuclear prefix reset will NOT clear such config; if a bad config value causes the failure, the reset appears to "not work." Check the game directory for config/savedata files before concluding the prefix reset failed.
- **Reversal:** n/a (diagnostic guidance)
- **Source:** Local debugging session (Binary Domain `UserCFG.txt`), 2026-05/06
- **Confirmations:** 1
- **Suspected mechanism:** Confirmed — game uses working-directory-relative config path
