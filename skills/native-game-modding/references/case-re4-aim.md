# Case: RE4 (2005, PC/UHD) — centred reticle and gun convergence

Repo: TuxLux40/re4uhd-modern-controls. It is a 32-bit `xinput1_3.dll` proxy running under Proton.

## Goal

A centred reticle, like the remakes, with the gun visibly pointing at what the reticle marks and a laser running
from the gun into the reticle.

## Dead end (2026-10-29): steering the gun with a model through the sway value

**What was tried.** The gun was turned onto the aim point through the per-frame aim sway's outputs:
- the arm's vertical blend value;
- the aim's sideways value `cPlayer+0x448`.

Three layers were stacked on top of each other:
1. a learnt shoulder-pivot model (from where two laser lines crossed);
2. a mapping constant;
3. a closed-loop trim on the model's leftover error.

The laser was also bent to the reticle, and its start was patched back onto the gun.

**What broke, one fix after another.**
- The laser detached from the gun.
- The pitch mapping was wrong (the game's 2/π factor implies 90° per unit; 60° was measured).
- Jitter at depth edges.
- The trim overshot while turning.
- The pivot was learnt for one weapon only.
- The shotgun hung high at the edge of the view.

**Root cause.** `+0x448` is the *sway* offset, meant for a few degrees. Twisting the upper body 30° through it
produced poses the game never authored. Each correction layer then added its own bug.

**Missed step.** No mechanism note was written first. The game aims sideways by turning Leon's whole heading
(`cPlayer+0xA0+4`), and that is the lever to use.

## Replacement design

- **Sideways:** a small heading offset on Leon, kept in its own variable. The camera follows the heading minus
  that offset (`AimGameYaw`), so it doesn't turn with it.
- **Vertical:** the arm blend value, 60° per unit, plus a feedback offset.
- **Feedback:** every frame the laser line (the gun's real line) is measured against the line from the laser
  sight to the aim point, and half the error is added. There is no model and no trim.
- **Laser:** not bent. It lands on the aim point because the gun does.
- **Aim point distance:** smoothed by its inverse with τ ≈ 0.12 s, with a minimum of 1000 units.

## Mechanism facts (verified in the log)

- **Arm pose controller** (`0xC7A7E8`):
  - `[0]` model, `[1]` value, `[2..4]` base/up/down motions;
  - motion layer at `+0x18`, weight `layer+200 = |v|`;
  - it switches the up/down motion only on a sign change of the value.
- **Raise setup functions,** one per weapon kind: `0x753660`, `0x8FCAA0`, `0x8FECB0`, `0x9152C0`, …
  - They load all three layer motions with the *raise* motion, so the arm value does nothing until live aim.
  - Live aim is `r_no` 6/1/0, about 0.35–0.55 s after the raise starts.
  - Fix: learn the live aim's up/down motions per (raise motion, weapon) and put them in during the raise.
- **LaserUpdate** (`0x73EA60`):
  1. line function `0x73DC60` (start, end);
  2. line hit `0x5BC050` truncates end;
  3. start pushed 500 units along the beam (`0xB26CB4`);
  4. draw effect `0x5FF940`.
