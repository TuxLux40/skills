# Cutover and rollback

The cutover is the moment the business starts using the new thing. A *deployment* releases software into an environment; a *cutover* moves the business — freezing activity, migrating live data, switching interfaces, communicating, deciding go/no-go, and keeping a way back. Decide the strategy before you write the runbook, because it sets how long the outage is and how far a failure spreads.

## Pick the cutover strategy

| | Big bang | Phased | Parallel run | Pilot |
|---|---|---|---|---|
| **How** | everyone/everything moves in one window | modules/regions/units move in waves | old + new run side by side, outputs compared | one site/group goes first, rest follow once stable |
| **Outage** | one longer window (often a holiday weekend) | several shorter windows | little/none, but data is entered or synced twice | short window per site |
| **Main risk** | an escaped defect hits the whole business at once | temporary old↔new interfaces become a defect source | fatigue; disputes over which system is right | an unrepresentative pilot, so later waves hit new problems |
| **Fits when** | data so coupled that temporary interfaces cost more than the outage | modules/regions have clean boundaries & different readiness | outputs compare mechanically (payroll, billing) | sites run similar processes; one can absorb early disruption |

Strategies combine — a phased programme often runs each wave as a small big-bang. **Related patterns:** *strangler-fig* (route traffic item-by-item from old to new behind a façade until the old is empty, then delete it — the safest way to replace a live system incrementally) and *blue-green* (two identical environments, switch traffic, switch back if needed). Both shrink the outage to a routing switch at the cost of running two systems and syncing them.

**Near-zero-downtime** is possible (parallel run, change-data-capture keeping new in sync, blue-green) but the price is complexity: sync logic, reconciling two live systems, harder rollback. For tightly-coupled systems a short planned outage is often the safer trade.

## The cutover sequence

**Change & data freeze → final extract/load → reconciliation checkpoint → technical smoke tests → go/no-go → open to users (→ hypercare).**

Freezes come in layers: master data freezes days ahead (urgent changes keyed into both systems); transactions freeze when the window opens. Decide what the business does *during* the outage — every paper form or queued order gets keyed in afterwards by a named owner.

## Build the runbook and rehearse until the timings are real

1. **Inventory every task** from the start of the freeze to business sign-off — stopping interfaces, backups, loads, routing/DNS changes, access, supplier-owned tasks.
2. **Assign one owner (+ backup), dependencies and a duration to each.** Mark the **critical path** — that chain sets the window length.
3. **Mock cutover** against a copy of production in a production-like environment; **time every task.** Expect missing steps, wrong order, scripts that only worked on small files.
4. **Fix, re-time, repeat.** The final rehearsal uses the **real people, at the real time of day, against the latest production copy.** Significant go-lives need at least two complete rehearsals; if the last one threw new defects or overran, do another rather than go live on hope.
5. **Add a reconciliation checkpoint after each major load and a contingency buffer before go/no-go.** If the measured plan doesn't fit the window, change scope or strategy *now*.
6. **Put the runbook under change control** after the last rehearsal — every late edit needs approval and a note of the risk it adds. Untested late edits cause most surprises on the night.

## Go/no-go — criteria with named evidence, decided in advance

Write each criterion as a check with named evidence. Decision group: sponsor + programme manager + technical lead + future operations owner, **one person holds the final vote.**

- Blocking reconciliation break nobody can explain yet → **no-go** (or investigate within the buffer). Opening on unexplained data turns a delay into a data-quality incident.
- Everything passes except known defects with agreed workarounds → **go**, and brief the workarounds to super-users before anyone logs in. (Criteria should demand defects are *understood and owned*, not that there are none.)
- Runbook is late but every checkpoint passed → spend the buffer; no-go only if the critical path would hit the point of no return too late. (Lateness is scheduling; failed checks are quality.)
- A critical-path supplier/infra dependency unconfirmed → **no-go until confirmed in writing.**

## Rollback — write it before you start

- **Can this be reversed, and for how long?** Identify the **point of no return** — the step after which going back means data loss or a forward-fix only (e.g. source deleted, domain released, number ported, target overwritten with new writes). Mark it ⚠ in the runbook.
- **Triggers to go back**, named in advance: which failed checks, error rates, or missed checkpoints mean rollback — not a judgement call at 3am.
- **The way back is tested too.** An untested rollback is not a plan. Rehearse it at least once.
- **What's lost in a rollback?** If users created data in the new system during the window, rolling back destroys it — decide how that's captured and re-keyed.
- Keep the **source intact and read-only** until after the point of no return is safely past and reconciliation holds.

## If a domain/DNS is involved

Lower the **TTL** on the records you'll change **days ahead** (so the change propagates in minutes, not hours). Change records at the start of the window; verify with `dig`/`nslookup` from multiple resolvers. For mail, a backup-MX/queueing service avoids bounces during the switch. Keep the old endpoint serving until traffic has fully moved to the new one. Releasing/transferring the domain itself is a ⚠ one-way, slow step — do it last.

## After: hypercare, then decommission

Run a **hypercare** period — heightened support, daily issue triage, the source still available — before you call it done. Exit hypercare on metrics (ticket volume back to normal, no open blockers), then decommission the source deliberately.
