---
name: native-game-modding
description: Use when modding a native (C/C++) PC game through hooks or a proxy DLL (xinput1_3, dinput8, version, winmm) — especially gameplay changes like camera, controls, aiming, movement or animation — and when working from a decompile (Ghidra dump, REA, IDA). Also on Linux/Proton. Enforces mechanism-first design, a design gate, a project knowledge file and a circuit breaker so fixes don't pile up into dead ends.
---

# Native game modding

Workflow for gameplay mods hooked into a native game. Its point is to stop the costly failure mode: building a
model of how the game *should* work, then patching the model's errors one by one until each fix breaks
something else. The game's own code is the spec; read it first, drive its own controls, and verify against the
running game.

## Hard rules (gates)

1. **No design before a mechanism note.** Before changing how something behaves, write down how the game does it
   (Phase 1). "I think the game…" is not a note.
2. **Design gate.** A change to how the game looks or plays gets a 3–6 line design shown to the user before code:
   which game values it drives, what stays vanilla, how it will be verified.
3. **Circuit breaker.** Stop and go back to Phase 1 when either happens:
   - two fixes in a row each break something new;
   - the same failure shows up three times.
   Write a `dead_ends.md` entry and tell the user plainly what was wrong with the approach. Don't add another
   correction layer.
4. **Use the tools you have.** For binary questions, use the REA skill/MCP (`reverse-engineer-anything`):
   decompile, callers, xrefs. If it isn't connected, grep the Ghidra dump. Before assuming a function is *the*
   one, list every caller of the helper it calls: games often have one variant per weapon, character or state.

## Phase 0 — load the project's knowledge

Before touching code, read these files in the mod repo; create them from `references/templates.md` if missing:

- `MODLOG.md`: the journal. Paths, build/install commands, addresses, what was verified and how.
- `docs/mechanics/<subsystem>.md`: how the game does it (Phase 1 output). One file per subsystem: aim, camera,
  movement, animation, inventory, and so on.
- `dead_ends.md`: approaches that failed and why. Read this before proposing anything.

Anything not in these files is lost at the next context compaction.

## Phase 1 — mechanism note (from the decompile, not from memory)

For the subsystem you are about to change, find and write down:

- **Entry points and variants.** The per-frame function, the state setup functions, and *all* sibling variants.
  Get these from the callers of the shared helper.
- **The state machine.** The state bytes (e.g. `r_no` routine numbers) and the order of states, with real
  timings from the log.
- **The game's controls.** Every value the game itself drives for this behaviour, what each is *meant* for and
  its normal range. Example: a sway offset meant for a few degrees is not a steering wheel for 30°.
- **Frame order.** Which code runs before which: input, state, animation and skeleton, effects (laser, muzzle),
  camera, render. Hooks that read last frame's data must know it.
- **Measured constants.** Scale factors confirmed in the log, e.g. "1.0 arm units ≈ 60° of gun pitch, measured;
  not the 90° the code's 2/π implies".

Confirm guesses at runtime (diag log, memory read) before building on them. Agents misidentify functions
confidently.

### Doing Phase 1 with REA (preferred) or the Ghidra dump

Condensed from the `reverse-engineer-anything` skill; read it for full tool details. REA tools are deferred MCP
tools (`mcp__rea__*`): load them with ToolSearch.

1. **Checklist first.** Turn the question into a list of things to answer and the evidence each needs, for
   example "which function sets the arm pose at the raise, for every weapon?" or "in which order do sway, laser
   and camera run in a frame?".
2. **Reuse state.** Call `binary_session` with `{}` first. If the game exe is already open, keep using it. Don't
   open a duplicate session or repeat an identical analysis.
3. **Open and orient.** Call `open_binary` on the game exe with provider `ghidra`. Find entry points with
   `search_strings` (debug strings, file names), `search_procedures` or a known address.
4. **Dossier.** `analyze_function` gives pseudocode, callers, callees, references and value flow in one call.
   For more detail, use `inspect_analysis_view` with its Evidence ID instead of re-running the analysis.
5. **Variants.** Call `procedure_callers` / `xrefs` on the shared helper (the pose init, the effect spawn, and
   so on). Use `build_call_path` / `trace_call_path` to place a function in the frame. Skipping this is how a
   fix lands for one weapon only.
6. **Make names stick.** Use `set_address_name` / `annotate_native_function` for whatever is understood, so
   later passes read named code instead of `FUN_00753660`. Put the same names into `docs/mechanics/`.
7. **Observed, inferred or unknown.** Mark every claim as one of these. Pseudocode is analysis, not source, and
   static analysis never shows what ran. A bounded search stays bounded: "no other callers found in X" is not
   "no other callers".
8. **Close the checklist.** Mark each question answered, partial or unresolved before designing. Then call
   `close_binary`.

**Fallback without REA.** If REA isn't connected, follow the same steps on the Ghidra text dump: `grep -n
"FUN_xxxx("` finds callers, and `awk` cuts out one function. Repair REA later with its connection guide rather
than skipping the analysis.

**Runtime confirmation under Proton.** Prefer the mod's own diag log: values plus ms since the event, read from
inside the game.
- Debuggers or Frida attached to a Wine process are fragile and may need ptrace rights the agent lacks
  (`ptrace_scope=1`).
- Use them only when the log can't answer, and only for single-player games without anti-cheat.

## Phase 2 — design

Check `references/gameplay-conventions.md` for how shipped modern games solve this, so you're not inventing a
convention. Then design with these principles:

- **Drive the game's own controls, inside their intended range.** Turn the character's heading, not a sway
  offset. Swap the motion a layer plays, not a bone by hand.
- **Measure and feed back instead of modelling.** If the game exposes the real result each frame (a laser line,
  a bone matrix, a hit point), correct by a share of the measured error. Don't build a learnt geometric model
  plus a trim to fix the model.
- **Keep game space and mod space apart.** When the mod adds an offset to a game value (a heading, an aim value),
  keep the offset in its own variable. Convert at the boundary, so the game's input handling and your camera
  never see your offset as player input.
- **Smallest vertical slice first.** One weapon, one state, all the way into the running game. Then widen.

Present the design (gate 2) and wait for the go when behaviour changes.

## Phase 3 — build and verify

- **Diagnostic log lines.** Add them with timestamps and ms-since-event for each phase of the behaviour, e.g.
  aim start, raise, live aim. Log the *inputs* of your decision (the game values) next to the outputs.
- **Read the log yourself.** Don't ask the user to repeat what they did. Check screenshots against the log;
  the running game is the oracle, not your reading of the code.
- **Restarting the game.** Follow the user's standing rules (memory) about when a restart is allowed.
- **Close out.** When something is confirmed, update `docs/mechanics/` and `MODLOG.md`. When it failed, add a
  `dead_ends.md` entry.

## Native hooking checklist (Windows game, also under Proton)

- **Proxy DLL.** Forward every export of the real DLL. Load the real one from the system dir, not via the search
  path.
- **Before each hook.** Check the bytes at the target against an expected signature, and log and skip on a
  mismatch (another game build). Hooks on shared helpers filter by return address to pick the one caller you
  mean.
- **Calling conventions.**
  - `__thiscall`: hook as `__fastcall(this, edx, …)`.
  - x87 `float10` returns from the decompile are plain floats/doubles at the ABI.
  - Decompiler "stack args" counts include `this` only for non-thiscall functions.
- **`windows.h` macros** break innocent names: `far`, `near`, `min`, `max`, `small`, `interface`. Rename locals.
- **Never overwrite the DLL while the game runs.** Under Wine it's mapped, so stop the game, copy, then `cmp`.
- **Logs.** Write to a log file next to the exe (truncate on start). Put the build/version on the first line, so
  a stale DLL is obvious.
- **Linux cross-builds.** zig/clang targeting `i386-windows-gnu` or `x86_64-windows-gnu` work without MSVC.
  Ignore clangd errors about a missing `windows.h` in the editor; the build is the truth.

## References

| File | Contents |
|------|----------|
| `references/gameplay-conventions.md` | How modern games do over-the-shoulder aim, a centred reticle, gun convergence, camera-relative movement, moving while aiming or reloading |
| `references/templates.md` | MODLOG.md, mechanics note, dead_ends.md templates |
| `references/case-re4-aim.md` | Worked dead end: RE4 (2005) gun convergence, what went wrong and the design that replaced it |

## Credits

Analysis workflow condensed from the `reverse-engineer-anything` (REA) skill. Process ideas adapted from [rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder)
(MIT): MODLOG journal, "read the real thing", the running game as the oracle, circuit breaker. Also from
[vgrichina/re-skill](https://github.com/vgrichina/re-skill) (MIT): dead-ends log and the stuck rule.
