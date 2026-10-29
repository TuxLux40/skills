# Gameplay conventions — how shipped games do it

Check this before designing a control, camera or aim change, so the mod matches what players already know and
doesn't invent its own convention.

## Over-the-shoulder aim with a centred reticle

Used by the RE2/3/4 remakes, The Last of Us, Gears of War, Uncharted and most modern third-person shooters.

**The reticle.** It is fixed at the screen centre and never moves.

**The aim point.** Cast a ray from the camera through the screen centre. Its first hit is the aim point.
- Start the ray at the character's depth, not at the camera eye. Otherwise walls or props between the camera
  and the character catch it.

**Shots.** Bullets travel from the muzzle to the aim point, or from the camera along the ray with the muzzle
only as the visual origin.
- Either way, the hit lands under the reticle.
- Spread and recoil scatter around the aim point, not around the barrel's own line.

**The gun's look (convergence).** The camera sits beside the gun, usually 30–60 cm right of the shoulder line,
so a gun held parallel to the view hits beside the aim point. Games close that gap visually:
- *Horizontal:* the character's body or heading turns a few degrees toward the aim point, or upper-body aim
  offsets do it. These are full-body animation blends authored for that range.
- *Vertical:* an aim pitch blend (aim-up, level and aim-down poses) or IK on the arms.
- *Smoothing:* the convergence distance is smoothed, and clamped to a minimum of about 1–2 m. When the reticle
  crosses an edge onto something nearer or farther, the gun eases over instead of snapping.
- *Laser sight (if any):* it runs straight from the muzzle and lands on or near the aim point because the gun
  converges. It isn't bent.

**Parallax is unavoidable.** With the eye off the gun line, the reticle and the gun's line meet at one depth
only. Convergence moves that depth to the aim point. Don't try to remove parallax by putting the camera on the
gun line: the character then blocks the centre of the screen.

**Raising the gun.** Modern games raise straight to the current camera pitch: the raise animation is blended
with the aim-pitch pose from its first frame. Older games often raise level and then tilt. If the mod centres
the view, that tilt reads as a jump.

**Camera.**
- The aim camera orbits a shoulder pivot. Looking up or down circles the pivot, so the character keeps its place
  on screen.
- The FOV narrows slightly (about 5–10°) when aiming.
- Recoil and breathing move the gun, not the camera, or move the camera only a little and then recover.

**Hand-back.** When the aim ends, the free camera continues from the aim view's direction with no snap. Exclude
any automatic turns the mod made, such as an aim-assist lock or convergence heading, so repeated aims don't drift.

## Movement (replacing tank controls)

**Camera-relative movement.** Stick up moves toward where the camera looks.
- Forward = the camera's forward vector flattened onto the ground plane.
- Right = forward × up. A wrong sign here is the classic "left and right swapped" bug.

**Turning.** The character turns toward the move direction at a capped turn speed. They don't snap.

**Aiming while moving.** The character faces the aim direction and strafes or backpedals with the stick at a
reduced speed (about 40–60 %).

**Reloading and shooting while moving.**
- The upper-body action runs as an additive or masked layer while the legs keep the locomotion state.
- If the engine can't layer, keep the character in its stand-still action state and move the root position
  yourself, with collision.

**Free camera.**
- The right stick orbits.
- The camera collides with walls and pulls in.
- It optionally recentres behind the character after a few seconds of running.

## Interaction and UI

- **Context prompts** show the button glyph of the active input device.
- **The reticle** changes colour or shape when it is over something damageable. Use the game's own "can be hit"
  test if it has one.
